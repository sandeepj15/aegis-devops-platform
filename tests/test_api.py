def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "environment" in data
    assert "version" in data
    assert "hostname" in data
    assert "timestamp" in data
    assert "X-Request-ID" in response.headers


def test_healthz_default_healthy(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_readyz_default_ready(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_simulate_unhealthy_and_reset(client):
    # Simulate failure
    post_res = client.post("/simulate/unhealthy")
    assert post_res.status_code == 200

    # Probe should return 503
    health_res = client.get("/healthz")
    assert health_res.status_code == 503
    assert health_res.json() == {"status": "unhealthy"}

    # Reset
    reset_res = client.post("/simulate/reset")
    assert reset_res.status_code == 200

    # Probe should return 200 again
    recovered_res = client.get("/healthz")
    assert recovered_res.status_code == 200
    assert recovered_res.json() == {"status": "healthy"}


def test_simulate_unready_and_reset(client):
    # Simulate unready
    post_res = client.post("/simulate/unready")
    assert post_res.status_code == 200

    # Probe should return 503
    ready_res = client.get("/readyz")
    assert ready_res.status_code == 503
    assert ready_res.json() == {"status": "not ready"}

    # Reset
    reset_res = client.post("/simulate/reset")
    assert reset_res.status_code == 200

    # Probe should return 200 again
    recovered_res = client.get("/readyz")
    assert recovered_res.status_code == 200
    assert recovered_res.json() == {"status": "ready"}


def test_info_endpoint(client):
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "version" in data
    assert "hostname" in data
    assert "environment" in data
    env = data["environment"]
    assert "APP_ENV" in env
    assert "APP_MESSAGE" in env
    assert "POD_NAME" in env
    assert "POD_NAMESPACE" in env
    assert "POD_IP" in env


def test_metrics_endpoint(client):
    # Trigger a request first to generate counter metric
    client.get("/")

    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text


def test_request_id_custom_propagation(client):
    custom_id = "test-custom-trace-12345"
    response = client.get("/", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id


def test_404_error_handling(client):
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["status_code"] == 404
    assert "request_id" in data
    assert response.headers.get("X-Request-ID") == data["request_id"]
