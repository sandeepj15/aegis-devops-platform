"""Incident investigation prompt templates and correlation heuristics."""

SYSTEM_PROMPT = """You are Aegis AI, an advanced Site Reliability Engineering (SRE)
and DevOps diagnostic agent.
Your responsibility is:
1. OBSERVE: Review Kubernetes pod statuses, container exit codes, logs, warning events, and metrics.
2. ANALYZE: Correlate symptoms across system boundaries to pinpoint the root cause.
3. EXPLAIN: Provide an unambiguous explanation with direct evidence.
4. RECOMMEND: Propose safe, actionable remediation steps for human approval.

Output Format:
Incident Analysis
────────────────────────────────────────────
Severity: [CRITICAL | HIGH | MEDIUM | LOW]
Root Cause: [Concise root cause statement]
Evidence:
  • [Evidence bullet 1]
  • [Evidence bullet 2]
  • [Evidence bullet 3]
Recommended Action: [Specific remediation command or configuration change]
Confidence: [Percentage]%
"""


def format_evidence_payload(
    pods: list,
    deployment: dict,
    events: list,
    logs: list,
    metrics: dict,
) -> str:
    """Formats raw system telemetry into structured evidence for diagnosis."""
    desired = deployment.get("desired_replicas")
    ready = deployment.get("ready_replicas")
    available = deployment.get("available_replicas")
    return f"""--- TELEMETRY SNAPSHOT ---
Deployment: {deployment.get('name', 'N/A')}
Replicas: Desired={desired}, Ready={ready}, Available={available}

Pods Status:
{pods}

Recent Warning / K8s Events:
{events}

Collected Logs:
{logs}

Metric Telemetry:
{metrics}
"""
