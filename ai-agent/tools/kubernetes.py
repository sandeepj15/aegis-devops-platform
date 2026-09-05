import json
import subprocess
from typing import Any, Optional


def _run_kubectl(args: list[str]) -> dict[str, Any]:
    """Helper to run kubectl and return parsed JSON output."""
    cmd = ["kubectl"] + args + ["-o", "json"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(res.stdout)
    except subprocess.CalledProcessError as e:
        return {"error": e.stderr.strip()}
    except Exception as e:
        return {"error": str(e)}


def get_pod_status(
    namespace: str = "aegis", selector: Optional[str] = None
) -> list[dict[str, Any]]:
    """Retrieves detailed status of pods in a namespace, optionally filtered by label selector."""
    args = ["get", "pods", "-n", namespace]
    if selector:
        args.extend(["-l", selector])
    data = _run_kubectl(args)
    if "error" in data:
        return [{"error": data["error"]}]

    pods_summary = []
    for item in data.get("items", []):
        meta = item.get("metadata", {})
        status = item.get("status", {})
        container_statuses = status.get("containerStatuses", [])

        restart_count = 0
        container_states = []
        is_ready = False

        for cs in container_statuses:
            restart_count += cs.get("restartCount", 0)
            if cs.get("ready"):
                is_ready = True
            state = cs.get("state", {})
            container_states.append(state)

        pods_summary.append({
            "name": meta.get("name"),
            "namespace": meta.get("namespace"),
            "phase": status.get("phase"),
            "is_ready": is_ready,
            "restart_count": restart_count,
            "pod_ip": status.get("podIP"),
            "container_states": container_states,
        })
    return pods_summary


def get_deployment(name: str = "aegis-api", namespace: str = "aegis") -> dict[str, Any]:
    """Retrieves deployment specification and operational status."""
    data = _run_kubectl(["get", "deployment", name, "-n", namespace])
    if "error" in data:
        return {"error": data["error"]}

    spec = data.get("spec", {})
    status = data.get("status", {})
    template = spec.get("template", {})
    containers = template.get("spec", {}).get("containers", [])

    container_details = []
    for c in containers:
        container_details.append({
            "name": c.get("name"),
            "image": c.get("image"),
            "resources": c.get("resources", {}),
            "liveness_probe": c.get("livenessProbe"),
            "readiness_probe": c.get("readinessProbe"),
            "env_vars": [e.get("name") for e in c.get("env", [])],
        })

    return {
        "name": name,
        "namespace": namespace,
        "desired_replicas": spec.get("replicas"),
        "ready_replicas": status.get("readyReplicas", 0),
        "available_replicas": status.get("availableReplicas", 0),
        "containers": container_details,
    }


def get_service(name: str = "aegis-service", namespace: str = "aegis") -> dict[str, Any]:
    """Retrieves service configuration and endpoint mapping."""
    data = _run_kubectl(["get", "service", name, "-n", namespace])
    if "error" in data:
        return {"error": data["error"]}

    spec = data.get("spec", {})
    return {
        "name": name,
        "namespace": namespace,
        "type": spec.get("type"),
        "cluster_ip": spec.get("clusterIP"),
        "selector": spec.get("selector"),
        "ports": spec.get("ports"),
    }
