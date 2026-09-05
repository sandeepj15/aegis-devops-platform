
from fastapi import APIRouter, Response, status

router = APIRouter(tags=["Health & Probes"])

# In-memory probe state for Kubernetes self-healing and failure testing
probe_state: dict[str, bool] = {
    "is_healthy": True,
    "is_ready": True,
}


@router.get("/healthz", summary="Liveness Probe", status_code=status.HTTP_200_OK)
def healthz(response: Response) -> dict[str, str]:
    """Kubernetes liveness probe endpoint.

    Fails with HTTP 503 if marked unhealthy.
    """
    if not probe_state["is_healthy"]:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy"}
    return {"status": "healthy"}


@router.get("/readyz", summary="Readiness Probe", status_code=status.HTTP_200_OK)
def readyz(response: Response) -> dict[str, str]:
    """Kubernetes readiness probe endpoint.

    Fails with HTTP 503 if marked unready, removing pod from service endpoints.
    """
    if not probe_state["is_ready"]:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not ready"}
    return {"status": "ready"}


@router.post("/simulate/unhealthy", summary="Simulate Liveness Failure")
def simulate_unhealthy() -> dict[str, str]:
    """Simulates application crash / liveness probe failure."""
    probe_state["is_healthy"] = False
    return {"message": "Liveness probe set to unhealthy (HTTP 503)"}


@router.post("/simulate/unready", summary="Simulate Readiness Failure")
def simulate_unready() -> dict[str, str]:
    """Simulates dependency drop / readiness probe failure."""
    probe_state["is_ready"] = False
    return {"message": "Readiness probe set to not ready (HTTP 503)"}


@router.post("/simulate/reset", summary="Reset Probe Simulation")
def simulate_reset() -> dict[str, str]:
    """Resets probes back to healthy and ready state."""
    probe_state["is_healthy"] = True
    probe_state["is_ready"] = True
    return {"message": "Probes reset to healthy and ready"}
