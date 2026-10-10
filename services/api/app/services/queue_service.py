import asyncio
import json
import logging
from typing import Any, Callable, Dict, Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)


class TaskQueue:
    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None
        self._local_queue: asyncio.Queue = asyncio.Queue()
        self._workers: list = []
        self._running = False

    async def initialize(self):
        self._running = True
        if settings.REDIS_ENABLED:
            try:
                self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
                await self._redis.ping()
                logger.info("Connected to Redis task queue.")
            except Exception as e:
                logger.warning(f"Redis unavailable ({str(e)}). Falling back to in-process async queue.")
                self._redis = None

        # Start 2 local background queue consumer workers
        for i in range(2):
            w = asyncio.create_task(self._worker_loop(i))
            self._workers.append(w)

    async def enqueue(self, task_name: str, payload: Dict[str, Any]):
        """Enqueue task into Redis or local async queue."""
        task_data = {
            "task": task_name,
            "payload": payload
        }
        if self._redis:
            try:
                await self._redis.rpush("sentinel:tasks", json.dumps(task_data))
                return
            except Exception as e:
                logger.error(f"Failed to push to Redis: {str(e)}, falling back to memory queue.")

        await self._local_queue.put(task_data)

    async def _worker_loop(self, worker_id: int):
        while self._running:
            try:
                # Prioritize local queue or poll Redis
                task_data = None
                if self._redis:
                    raw = await self._redis.blpop("sentinel:tasks", timeout=1)
                    if raw:
                        _, val = raw
                        task_data = json.loads(val)
                
                if not task_data:
                    try:
                        task_data = await asyncio.wait_for(self._local_queue.get(), timeout=1.0)
                    except asyncio.TimeoutError:
                        continue

                task_name = task_data.get("task")
                payload = task_data.get("payload", {})
                logger.info(f"[Worker-{worker_id}] Processing {task_name}: {payload}")

                # Dispatch scan task
                if task_name == "run_scan":
                    from app.core.database import AsyncSessionLocal
                    from app.services.scan_service import ScanService

                    scan_id = payload.get("scan_id")
                    target_path = payload.get("target_path")
                    diff_text = payload.get("diff_text")

                    async with AsyncSessionLocal() as session:
                        await ScanService.execute_scan(
                            db=session,
                            scan_id=scan_id,
                            target_path=target_path,
                            diff_text=diff_text,
                        )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Worker-{worker_id}] Error in worker loop: {str(e)}", exc_info=True)
                await asyncio.sleep(1)

    async def shutdown(self):
        self._running = False
        for w in self._workers:
            w.cancel()
        if self._redis:
            await self._redis.close()


task_queue = TaskQueue()
