#!/usr/bin/env bash
set -e

echo "Cleaning up Aegis platform resources..."

# 1. Delete application manifests
kubectl delete -f k8s/ --ignore-not-found=true

# 2. Delete NGINX Ingress Controller
kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.1/deploy/static/provider/cloud/deploy.yaml --ignore-not-found=true

# 3. Delete Argo CD
kubectl delete -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml -n argocd --ignore-not-found=true
kubectl delete namespace argocd --ignore-not-found=true

# 4. Remove project TLS certificates
rm -rf certs/

# 5. Remove local Docker image
docker rmi aegis-api:dev 2>/dev/null || true

echo "Cleanup complete."