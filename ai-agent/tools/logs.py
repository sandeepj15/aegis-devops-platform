import subprocess


def get_pod_logs(pod_name: str, namespace: str = "aegis", tail_lines: int = 50) -> dict[str, str]:
    """Retrieves stdout/stderr log output from a Kubernetes pod."""
    cmd = ["kubectl", "logs", pod_name, "-n", namespace, f"--tail={tail_lines}"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"pod": pod_name, "logs": res.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"pod": pod_name, "error": e.stderr.strip()}
    except Exception as e:
        return {"pod": pod_name, "error": str(e)}
