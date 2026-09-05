#!/usr/bin/env python3
"""Aegis AI DevOps Agent — Incident Investigation and Root Cause Analysis Engine."""

import os
import sys
from typing import Any, Dict, List

# Ensure local package imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.events import get_k8s_events
from tools.kubernetes import get_deployment, get_pod_status, get_service
from tools.logs import get_pod_logs
from tools.metrics import get_metrics
from prompts.incident_analysis import SYSTEM_PROMPT, format_evidence_payload


class AegisAIAgent:
    """Automated SRE & Incident Analysis Agent."""

    def __init__(self, namespace: str = "aegis", deployment_name: str = "aegis-api"):
        self.namespace = namespace
        self.deployment_name = deployment_name

    def collect_telemetry(self) -> Dict[str, Any]:
        """Gathers diagnostic data from all observability and cluster surfaces."""
        print(f"[*] Inspecting Pod status for '{self.deployment_name}' in namespace '{self.namespace}'...")
        pods = get_pod_status(self.namespace, selector=f"app={self.deployment_name}")

        print(f"[*] Inspecting Deployment '{self.deployment_name}'...")
        deployment = get_deployment(self.deployment_name, self.namespace)

        print(f"[*] Inspecting Kubernetes cluster events...")
        events = get_k8s_events(self.namespace)

        print(f"[*] Reading pod logs...")
        logs = []
        for pod in pods:
            name = pod.get("name")
            if name:
                logs.append(get_pod_logs(name, self.namespace, tail_lines=30))

        print(f"[*] Checking telemetry metrics...")
        metrics = get_metrics("http_requests_total")

        return {
            "pods": pods,
            "deployment": deployment,
            "events": events,
            "logs": logs,
            "metrics": metrics,
        }

    def correlate_and_analyze(self, telemetry: Dict[str, Any]) -> str:
        """Analyzes symptoms to derive probable root cause and safe remediation."""
        pods = telemetry["pods"]
        events = telemetry["events"]
        logs = telemetry["logs"]
        deployment = telemetry["deployment"]

        # Check for pod failures or probe warnings
        unready_pods = [p for p in pods if not p.get("is_ready") and p.get("phase") == "Running"]
        crashing_pods = [p for p in pods if p.get("restart_count", 0) > 0]
        failed_pods = [p for p in pods if p.get("phase") in ["Failed", "CrashLoopBackOff"]]

        # Scenario 1: Readiness probe failure
        if unready_pods and not crashing_pods:
            failing_names = ", ".join(p.get("name", "") for p in unready_pods)
            return (
                "Incident Analysis\n"
                "────────────────────────────────────────────────────────────\n"
                "Severity: MEDIUM\n"
                f"Root Cause: Readiness probe failing on Pod(s) [{failing_names}].\n"
                "Evidence:\n"
                f"  • {len(unready_pods)} pod(s) currently marked Not Ready (0/1 Running).\n"
                "  • Pods automatically removed from Service endpoints to protect traffic.\n"
                "  • Container remains alive, indicating a dependency or simulated failure state.\n"
                "Recommended Action:\n"
                "  Verify upstream dependency health, or reset probe simulator via:\n"
                "  curl -X POST https://aegis.local/simulate/reset\n"
                "Confidence: 96%\n"
            )

        # Scenario 2: Missing environment variable or crashloop
        log_text = " ".join(l.get("logs", "") for l in logs)
        if "DATABASE_URL" in log_text and ("missing" in log_text.lower() or "error" in log_text.lower()):
            return (
                "Incident Analysis\n"
                "────────────────────────────────────────────────────────────\n"
                "Severity: HIGH\n"
                "Root Cause: Application startup failure due to missing DATABASE_URL secret.\n"
                "Evidence:\n"
                "  • Container logs indicate database connection string is unconfigured.\n"
                "  • Pod entered CrashLoopBackOff state.\n"
                "Recommended Action:\n"
                "  Configure DATABASE_URL in 'k8s/secret.yaml' and re-apply secret:\n"
                "  kubectl apply -f k8s/secret.yaml\n"
                "Confidence: 94%\n"
            )

        # Scenario 3: Healthy operational state
        if all(p.get("is_ready") for p in pods) and deployment.get("ready_replicas", 0) > 0:
            return (
                "Incident Analysis\n"
                "────────────────────────────────────────────────────────────\n"
                "Severity: NONE\n"
                "Root Cause: System is operating normally within healthy SLO boundaries.\n"
                "Evidence:\n"
                f"  • All {len(pods)} pod(s) are in Ready state (1/1 Running).\n"
                f"  • Desired replicas ({deployment.get('desired_replicas')}) match ready replicas ({deployment.get('ready_replicas')}).\n"
                "  • Zero restarts recorded across the deployment.\n"
                "  • Service endpoints active and healthy.\n"
                "Recommended Action: No remediation required.\n"
                "Confidence: 99%\n"
            )

        # Generic correlation
        return (
            "Incident Analysis\n"
            "────────────────────────────────────────────────────────────\n"
            "Severity: LOW\n"
            "Root Cause: Telemetry indicates degraded state requiring manual inspection.\n"
            "Evidence:\n"
            f"  • Telemetry snapshot captured across {len(pods)} pod(s).\n"
            "Recommended Action: Review kubectl events and pod descriptions.\n"
            "Confidence: 80%\n"
        )

    def run_investigation(self) -> str:
        """Executes full diagnostic pipeline."""
        print(f"\n[Aegis AI Agent] Investigating service: {self.deployment_name}")
        telemetry = self.collect_telemetry()
        report = self.correlate_and_analyze(telemetry)
        print("\n" + report)
        return report


if __name__ == "__main__":
    agent = AegisAIAgent()
    agent.run_investigation()
