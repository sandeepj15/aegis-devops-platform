import pytest
from fastapi.testclient import TestClient

from app.app import app
from app.routes.probes import probe_state


@pytest.fixture(autouse=True)
def reset_probe_state():
    """Ensure clean probe state before each test execution."""
    probe_state["is_healthy"] = True
    probe_state["is_ready"] = True
    yield
    probe_state["is_healthy"] = True
    probe_state["is_ready"] = True


@pytest.fixture
def client():
    """Test client fixture for API requests."""
    with TestClient(app) as test_client:
        yield test_client
