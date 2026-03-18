#!/usr/bin/env bash
set -euo pipefail

kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-db-secret.yaml
kubectl apply -f 02-db-pvc.yaml
kubectl apply -f 03-db-service.yaml
kubectl apply -f 04-db-statefulset.yaml
kubectl apply -f 06-backend-service.yaml
kubectl apply -f 05-backend-deployment.yaml
kubectl apply -f 07-frontend-deployment.yaml
kubectl apply -f 08-frontend-service.yaml

echo "All manifests applied."
kubectl -n smart-interviewer get pods,svc,pvc
