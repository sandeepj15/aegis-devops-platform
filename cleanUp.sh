#!/usr/bin/env bash
set -e

# Terminal colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${YELLOW}Cleaning up Aegis platform resources...${NC}"

# 1. Delete Argo CD Application and remove finalizers
echo "Removing Argo CD Application..."
kubectl patch application aegis -n argocd -p '{"metadata":{"finalizers":null}}' --type=merge >/dev/null 2>&1 || true
kubectl delete -f argocd/application.yaml --ignore-not-found=true >/dev/null 2>&1 || true
kubectl delete -f argocd/ingress.yaml --ignore-not-found=true >/dev/null 2>&1 || true

# 2. Delete application and observability workloads
echo "Removing Aegis workloads, Prometheus, Grafana, and Loki..."
kubectl delete -f monitoring/loki/loki.yaml --ignore-not-found=true >/dev/null 2>&1 || true
kubectl delete -f monitoring/grafana/grafana.yaml --ignore-not-found=true >/dev/null 2>&1 || true
kubectl delete -f monitoring/prometheus/prometheus.yaml --ignore-not-found=true >/dev/null 2>&1 || true
kubectl delete -f k8s/ --ignore-not-found=true >/dev/null 2>&1 || true
kubectl delete namespace aegis --ignore-not-found=true >/dev/null 2>&1 || true

# 3. Delete NGINX Ingress Controller
echo "Removing NGINX Ingress Controller..."
kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.1/deploy/static/provider/cloud/deploy.yaml --ignore-not-found=true >/dev/null 2>&1 || true

# 4. Delete Argo CD control plane
echo "Removing Argo CD control plane..."
kubectl delete -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml -n argocd --ignore-not-found=true >/dev/null 2>&1 || true
kubectl delete namespace argocd --ignore-not-found=true >/dev/null 2>&1 || true

# 5. Delete metrics-server
echo "Removing metrics-server..."
kubectl delete -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml --ignore-not-found=true >/dev/null 2>&1 || true

# 6. Remove project TLS certificates
echo "Removing generated TLS certificates..."
rm -rf certs/

# 7. Remove local Docker image
echo "Removing local Docker image..."
docker rmi aegis-api:dev >/dev/null 2>&1 || true

echo -e "${GREEN}Cleanup complete! Cluster restored to baseline.${NC}"