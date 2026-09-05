# Aegis — AI-Powered GitOps DevOps Platform

An end-to-end DevOps platform demonstrating modern software delivery, Kubernetes operations, GitOps, observability, security automation, and AI-assisted incident analysis.

The project is designed to run locally on macOS using Docker Desktop Kubernetes and does not require AWS, EKS, or cloud infrastructure.

---

## 1. Project Overview

Aegis demonstrates a production-style application delivery workflow:

```text
Developer
   │
   │ git push
   ▼
GitHub
   │
   ▼
GitHub Actions
   ├── Unit Tests
   ├── Lint (Ruff)
   ├── Security Scanning (Bandit, Gitleaks)
   ├── Docker Build
   └── Image Vulnerability Scan (Trivy)
   │
   ▼
GitHub Container Registry (GHCR)
   │
   ▼ (GitOps Manifest Update)
GitHub
   │
   ▼ (Watches Git)
Argo CD
   │
   ▼ (Reconciles State)
Docker Desktop Kubernetes
   ├── Ingress (NGINX)
   ├── FastAPI Service & Deployment
   ├── PostgreSQL
   ├── Redis
   └── Background Worker
   │
   ▼
Observability
   ├── Prometheus (Metrics)
   ├── Grafana (Dashboards)
   └── Loki (Centralized Logs)
   │
   ▼
AI DevOps Agent
   ├── Log Analysis
   ├── Kubernetes Event Analysis
   ├── Metric Correlation
   ├── Root Cause Analysis
   └── Controlled Remediation
```

---

## 2. Core Capabilities Demonstrated

- **Application Architecture**: FastAPI with structured JSON logging, Pydantic settings, request tracing, and Prometheus metrics.
- **Docker Containerization**: Multi-stage, non-root user, slim base images, and container healthchecks.
- **Kubernetes Operations**: Deployments, Services, ConfigMaps, Secrets, Ingress, HPA, and Liveness/Readiness/Startup probes.
- **Continuous Integration (CI)**: GitHub Actions executing Ruff, Pytest, Bandit, Gitleaks, Docker builds, and Trivy scans.
- **Package Management**: GitHub Container Registry (GHCR) using immutable Git SHA-based image tags.
- **GitOps Continuous Deployment**: Argo CD automated synchronization, drift detection, and self-healing.
- **Infrastructure as Code (IaC)**: Terraform managing Kubernetes platform infrastructure with clear boundary separation from GitOps.
- **Observability**: Prometheus metrics scraping, Loki log aggregation, and Grafana monitoring dashboards with custom alert rules.
- **AI-Assisted Operations**: AI Agent querying Pod status, events, logs, and metrics to perform root-cause analysis with human-in-the-loop approvals.
- **Failure Engineering**: Intentional disruption testing for crash looping, readiness drops, CPU spikes, and failed releases.

---

## 3. Technology Stack

- **Application**: Python 3.12, FastAPI, Uvicorn, Pydantic v2, Pytest, Prometheus Client
- **Containers**: Docker, GHCR
- **Orchestration**: Kubernetes (Docker Desktop), NGINX Ingress Controller
- **CI / CD**: GitHub Actions, Argo CD
- **Infrastructure as Code**: Terraform
- **Security & Quality**: Ruff, Bandit, Gitleaks, Trivy
- **Observability**: Prometheus, Grafana, Loki
- **AI Operations**: Python SDK / OpenAI-compatible diagnostic agent

---

## 4. Repository Structure

```text
aegis-devops-platform/
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── logging.py
│   ├── metrics.py
│   └── routes/
│       ├── __init__.py
│       ├── core.py
│       └── probes.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_api.py
├── k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── hpa.yaml
├── argocd/
│   └── application.yaml
├── terraform/
├── monitoring/
│   ├── prometheus/
│   ├── grafana/
│   └── loki/
├── ai-agent/
│   ├── agent.py
│   ├── tools/
│   └── prompts/
├── .github/
│   └── workflows/
│       ├── ci.yaml
│       └── build-publish.yaml
├── docs/
├── Dockerfile
├── requirements.txt
├── .dockerignore
└── .gitignore
```

---

## 5. Phased Roadmap

| Phase | Description | Status |
|---|---|---|
| **Phase 0** | Repository Scaffolding & Foundation | Completed |
| **Phase 1** | Production-Grade FastAPI Application & Pytest Suite | In Progress |
| **Phase 2** | Production Dockerfile (Non-root, slim, healthchecks) | Pending |
| **Phase 3** | Kubernetes Manifests (Probes, HPA, ConfigMaps, Secrets) | Pending |
| **Phase 4** | Local HTTPS Ingress (`mkcert` & `/etc/hosts`) | Pending |
| **Phase 5** | GitHub Actions CI Pipeline (Ruff, Pytest, Bandit, Trivy) | Pending |
| **Phase 6** | GitHub Container Registry (GHCR) Publishing | Pending |
| **Phase 7** | Argo CD Setup & Declarative GitOps Application | Pending |
| **Phase 8** | CI to GitOps Automatic Manifest Synchronization | Pending |
| **Phase 9** | GitOps Self-Healing & Drift Detection Experiments | Pending |
| **Phase 10** | Terraform Infrastructure as Code | Pending |
| **Phase 11** | Observability (Prometheus, Grafana, Loki) | Pending |
| **Phase 12** | Alerting & Incident Rules | Pending |
| **Phase 13** | AI DevOps Diagnostic Agent | Pending |
| **Phase 14** | AI Incident Investigation Scenarios | Pending |
| **Phase 15** | Failure Engineering & Chaos Testing | Pending |
| **Phase 16** | Controlled AI Remediation (Human-in-the-Loop) | Pending |
| **Phase 17** | End-to-End Portfolio Demonstration | Pending |
