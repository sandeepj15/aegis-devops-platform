import urllib.request
import json
from typing import Any, Dict


def get_metrics(query: str = "http_requests_total", prometheus_url: str = "http://localhost:9090") -> Dict[str, Any]:
    """Queries Prometheus metrics API or scrapes internal endpoint."""
    url = f"{prometheus_url}/api/v1/query?query={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Aegis-AI-Agent"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"query": query, "data": data.get("data", {}).get("result", [])}
    except Exception as e:
        return {"query": query, "warning": f"Prometheus unreachable at {prometheus_url}: {e}"}
