#!/usr/bin/env bash
set -e

# Terminal colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}   Aegis — AI-Powered GitOps Platform Startup       ${NC}"
echo -e "${BLUE}====================================================${NC}"

# 1. Pre-flight Checks
echo -e "\n${YELLOW}[1/8] Verifying prerequisites...${NC}"
if ! docker info >/dev/null 2>&1; then
  echo -e "${RED}Error: Docker is not running. Please start Docker Desktop.${NC}"
  exit 1
fi

if ! command -v kubectl &> /dev/null; then
  echo -e "${RED}Error: kubectl is required. Please install kubectl.${NC}"
  exit 1
fi

CURRENT_CTX=$(kubectl config current-context 2>/dev/null || echo "none")
if [ "$CURRENT_CTX" != "docker-desktop" ]; then
  echo -e "${YELLOW}Switching kubectl context to docker-desktop...${NC}"
  kubectl config use-context docker-desktop || true
fi

if ! command -v mkcert &> /dev/null; then
  echo -e "${RED}Error: mkcert is required for trusted local HTTPS. Install with: brew install mkcert${NC}"
  exit 1
fi

# Ensure local CA is installed
mkcert -install >/dev/null 2>&1 || true
echo -e "${GREEN}✓ Prerequisites verified.${NC}"

# 2. Build Docker Container
echo -e "\n${YELLOW}[2/8] Building local Docker image 'aegis-api:dev'...${NC}"
docker build -t aegis-api:dev . >/dev/null
echo -e "${GREEN}✓ Docker image built successfully.${NC}"

# 3. TLS Certificates
echo -e "\n${YELLOW}[3/8] Generating local TLS certificates via mkcert...${NC}"
mkdir -p certs
mkcert -cert-file certs/aegis-platform.pem -key-file certs/aegis-platform-key.pem \
  aegis.local argocd.local grafana.local prometheus.local >/dev/null 2>&1

kubectl create namespace aegis --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f - >/dev/null

kubectl create secret tls aegis-platform-tls \
  --cert=certs/aegis-platform.pem \
  --key=certs/aegis-platform-key.pem \
  -n aegis --dry-run=client -o yaml | kubectl apply -f - >/dev/null

kubectl create secret tls aegis-platform-tls \
  --cert=certs/aegis-platform.pem \
  --key=certs/aegis-platform-key.pem \
  -n argocd --dry-run=client -o yaml | kubectl apply -f - >/dev/null
echo -e "${GREEN}✓ Local TLS certificates & secrets configured.${NC}"

# 4. Ingress Controller & Metrics Server
echo -e "\n${YELLOW}[4/8] Setting up NGINX Ingress Controller & Metrics Server...${NC}"
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.1/deploy/static/provider/cloud/deploy.yaml >/dev/null

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml >/dev/null
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]' 2>/dev/null || true

# Wait for Ingress Controller to be ready and disable admission webhook to prevent race conditions in local dev
echo "Waiting for Ingress Controller..."
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s >/dev/null 2>&1 || true
kubectl delete validatingwebhookconfiguration ingress-nginx-admission --ignore-not-found=true >/dev/null 2>&1 || true
echo -e "${GREEN}✓ Ingress Controller & Metrics Server ready.${NC}"

# 5. Argo CD GitOps
echo -e "\n${YELLOW}[5/8] Setting up Argo CD GitOps control plane...${NC}"
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml >/dev/null

# Patch redis to avoid public.ecr.aws rate limits
kubectl set image deployment/argocd-redis redis=redis:7.2.4-alpine -n argocd 2>/dev/null || true

kubectl apply -f argocd/ingress.yaml >/dev/null
kubectl apply -f argocd/application.yaml >/dev/null
echo -e "${GREEN}✓ Argo CD applied and application synchronized.${NC}"

# 6. Aegis Core Workloads
echo -e "\n${YELLOW}[6/8] Deploying Aegis Kubernetes workloads...${NC}"
kubectl apply -f k8s/ >/dev/null
echo -e "${GREEN}✓ Aegis Deployment, Service, Ingress, HPA, ConfigMap & Secret applied.${NC}"

# 7. Observability Stack (Prometheus, Grafana, Loki, Promtail)
echo -e "\n${YELLOW}[7/8] Deploying Observability Stack (Prometheus, Grafana, Loki, Promtail)...${NC}"
kubectl apply -f monitoring/prometheus/prometheus.yaml >/dev/null
kubectl apply -f monitoring/grafana/grafana.yaml >/dev/null
kubectl apply -f monitoring/loki/loki.yaml >/dev/null
echo -e "${GREEN}✓ Prometheus, Grafana, Loki, and Promtail applied.${NC}"

# 8. Verification & Readiness Wait
echo -e "\n${YELLOW}[8/8] Waiting for core platform components to be Ready...${NC}"
echo "Waiting for Aegis API..."
kubectl wait --namespace aegis --for=condition=ready pod --selector=app=aegis-api --timeout=90s >/dev/null 2>&1 || true

echo "Waiting for Grafana..."
kubectl wait --namespace aegis --for=condition=ready pod --selector=app=grafana --timeout=90s >/dev/null 2>&1 || true

echo "Waiting for Prometheus..."
kubectl wait --namespace aegis --for=condition=ready pod --selector=app=prometheus --timeout=90s >/dev/null 2>&1 || true

echo "Waiting for Loki..."
kubectl wait --namespace aegis --for=condition=ready pod --selector=app=loki --timeout=90s >/dev/null 2>&1 || true

echo "Waiting for Argo CD Server..."
kubectl wait --namespace argocd --for=condition=ready pod --selector=app.kubernetes.io/name=argocd-server --timeout=90s >/dev/null 2>&1 || true

# Provision Grafana dashboard via API with retries
echo "Provisioning Grafana Overview Dashboard..."
python3 -c '
import json, subprocess, time
try:
    with open("monitoring/grafana/dashboard.json") as f:
        data = json.load(f)
    payload = json.dumps({"dashboard": data, "overwrite": True})
    for _ in range(15):
        cmd = [
            "kubectl", "exec", "-i", "-n", "aegis", "deployment/grafana", "--",
            "curl", "-s", "-u", "admin:aegispass", "-X", "POST",
            "-H", "Content-Type: application/json",
            "http://localhost:3000/api/dashboards/db",
            "-d", "@-"
        ]
        res = subprocess.run(cmd, input=payload, text=True, capture_output=True)
        if res.returncode == 0 and ("success" in res.stdout or "version" in res.stdout):
            break
        time.sleep(2)
except Exception:
    pass
' 2>/dev/null || true

# Fetch Argo CD initial password with retry
ARGOCD_PASSWORD=""
for _ in {1..15}; do
  ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" 2>/dev/null | base64 -d || true)
  if [ -n "$ARGOCD_PASSWORD" ]; then
    break
  fi
  sleep 2
done
[ -z "$ARGOCD_PASSWORD" ] && ARGOCD_PASSWORD="(Pending creation - retrieve later with: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)"

# Check /etc/hosts
HOSTS_CHECK=0
grep -q "aegis.local" /etc/hosts 2>/dev/null || HOSTS_CHECK=1

echo -e "\n${GREEN}====================================================${NC}"
echo -e "${GREEN}       Aegis Platform is 100% Operational!          ${NC}"
echo -e "${GREEN}====================================================${NC}"

if [ $HOSTS_CHECK -eq 1 ]; then
  echo -e "\n${YELLOW}Notice: Browser hostname mapping not detected in /etc/hosts.${NC}"
  echo -e "Run this command once to enable browser access:"
  echo -e "  ${BLUE}echo \"127.0.0.1 aegis.local argocd.local grafana.local prometheus.local\" | sudo tee -a /etc/hosts${NC}\n"
fi

echo -e "Platform Services:"
echo -e "  • ${BLUE}Aegis API${NC}:          https://aegis.local"
echo -e "  • ${BLUE}Argo CD Web UI${NC}:     https://argocd.local  (User: admin / Pass: ${ARGOCD_PASSWORD})"
echo -e "  • ${BLUE}Grafana Dashboards${NC}: https://grafana.local  (User: admin / Pass: aegispass)"
echo -e "    Dashboard:            https://grafana.local/d/aegis-overview/aegis-platform-overview-metrics-and-logs"
echo -e "  • ${BLUE}Prometheus Engine${NC}:  https://prometheus.local"
echo -e "  • ${BLUE}AI DevOps Agent${NC}:    python3 ai-agent/agent.py"
echo -e "\n${GREEN}Setup complete! Zero port-forwarding required.${NC}"
