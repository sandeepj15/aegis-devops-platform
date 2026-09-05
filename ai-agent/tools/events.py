import json
import subprocess
from typing import Any, Dict, List


def get_k8s_events(namespace: str = "aegis") -> List[Dict[str, Any]]:
    """Retrieves cluster events in a namespace sorted by recency."""
    cmd = ["kubectl", "get", "events", "-n", namespace, "-o", "json"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        events = []
        for item in data.get("items", []):
            events.append({
                "type": item.get("type"),
                "reason": item.get("reason"),
                "message": item.get("message"),
                "involved_object": item.get("involvedObject", {}).get("name"),
                "count": item.get("count", 1),
                "last_timestamp": item.get("lastTimestamp"),
            })
        return events
    except subprocess.CalledProcessError as e:
        return [{"error": e.stderr.strip()}]
    except Exception as e:
        return [{"error": str(e)}]
