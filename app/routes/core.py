import platform
import socket
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Response

from app.config import Settings, get_settings
from app.metrics import get_metrics_response

router = APIRouter(tags=["Core"])


@router.get("/", summary="Root Endpoint")
def get_root(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    """Root endpoint returning basic metadata and host information."""
    return {
        "message": settings.APP_MESSAGE,
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION,
        "hostname": socket.gethostname(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/info", summary="System & Pod Information")
def get_info(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    """Returns pod, runtime, and configuration details useful for verifying

    ConfigMaps and Downward API.
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "environment": {
            "APP_ENV": settings.APP_ENV,
            "APP_MESSAGE": settings.APP_MESSAGE,
            "PORT": settings.PORT,
            "POD_NAME": settings.POD_NAME,
            "POD_NAMESPACE": settings.POD_NAMESPACE,
            "POD_IP": settings.POD_IP,
        },
    }


@router.get("/metrics", summary="Prometheus Metrics")
def metrics_endpoint() -> Response:
    """Exposes Prometheus scrape metrics."""
    return get_metrics_response()
