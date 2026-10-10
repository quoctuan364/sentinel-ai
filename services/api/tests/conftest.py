import pytest_asyncio
from app.core.database import Base, engine
from app.main import seed_initial_data


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
