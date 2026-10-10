from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

router = APIRouter(tags=["Metrics"])

# Prometheus Metrics Definitions
SCAN_COUNT = Counter(
    "sentinel_scans_total",
    "Total number of scans triggered",
    ["status", "trigger"]
)
FINDINGS_COUNT = Counter(
    "sentinel_findings_total",
    "Total security findings detected",
    ["severity", "scanner"]
)
SCAN_DURATION_SECONDS = Histogram(
    "sentinel_scan_duration_seconds",
    "Duration of security scans in seconds",
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
)
ACTIVE_SCANS = Gauge(
    "sentinel_active_scans",
    "Currently running security scans"
)


@router.get("/metrics")
async def get_prometheus_metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
