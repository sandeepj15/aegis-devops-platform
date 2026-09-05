import time
import uuid
from collections.abc import Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.logging import request_id_ctx_var, setup_logging
from app.metrics import REQUEST_DURATION_SECONDS, REQUESTS_IN_PROGRESS, REQUESTS_TOTAL
from app.routes.core import router as core_router
from app.routes.probes import router as probe_router

settings = get_settings()
logger = setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Aegis — Production-grade DevOps backend designed for "
        "Kubernetes, GitOps, and Observability."
    ),
    version=settings.APP_VERSION,
)


@app.middleware("http")
async def request_lifecycle_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware managing request ID tracing, Prometheus metrics collection,

    and structured access logging.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    token = request_id_ctx_var.set(request_id)

    path = request.url.path
    method = request.method

    # Skip prometheus tracking on the metrics endpoint to prevent recursion/skew
    is_metrics = path == "/metrics"
    if not is_metrics:
        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).inc()

    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as exc:
        logger.exception("Unhandled error processing request: %s", exc)
        raise
    finally:
        latency = time.perf_counter() - start_time

        if not is_metrics:
            REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).dec()
            REQUEST_DURATION_SECONDS.labels(method=method, endpoint=path).observe(latency)
            REQUESTS_TOTAL.labels(method=method, endpoint=path, status_code=status_code).inc()

        logger.info(
            "HTTP Request Completed",
            extra={
                "props": {
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "latency_ms": round(latency * 1000, 2),
                }
            },
        )
        request_id_ctx_var.reset(token)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    request_id = request_id_ctx_var.get()
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = request_id_ctx_var.get()
    logger.exception("Internal Server Error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "status_code": 500,
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


# Include Routers
app.include_router(core_router)
app.include_router(probe_router)
