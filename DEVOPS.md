# DevOps Journey and Delivery Pipeline

This guide explains the complete DevOps implementation of Smart Voice Interviewer, phase by phase.
It covers architecture decisions, implementation details, incidents, root causes, fixes, CI/CD behavior, and rollback operations.

## 1. Executive Summary

Smart Voice Interviewer is deployed as a containerized full-stack application on a lightweight Kubernetes cluster (K3s) running on AWS EC2.

Delivery objectives achieved:

1. Infrastructure as code with reproducible provisioning.
2. Automated cluster bootstrap and application deployment.
3. CI/CD pipeline that builds, pushes, and deploys images.
4. Rollback pipeline for fast recovery to known-good images.
5. Operational documentation for repeatable release operations.

## 2. Final Target Topology

Core topology:

1. AWS EC2 master node: K3s control-plane.
2. AWS EC2 worker node: application workloads.
3. Kubernetes namespace: `smart-interviewer`.
4. Services:
  - PostgreSQL StatefulSet + ClusterIP service.
  - FastAPI backend Deployment + ClusterIP service.
  - React frontend Deployment + NodePort service (30080).

Traffic flow:

1. User browser -> `http://<MASTER_PUBLIC_IP>:30080`.
2. Frontend Nginx handles static assets.
3. Nginx proxies `/api/*` -> `backend-service:8000`.
4. Backend reads/writes PostgreSQL and performs semantic scoring.

## 3. Delivery Principles Used

1. Keep environments as similar as possible (containers everywhere).
2. Keep production config outside code where possible (GitHub secrets, env vars).
3. Favor immutable image tags (commit SHA) for traceable releases.
4. Design for failure: add rollback path before calling pipeline complete.
5. Stabilize first, optimize later (especially with t3.micro constraints).

## 4. Phase-by-Phase Implementation

## Phase 1 - Architecture Design

Artifacts:

1. `docs/architecture.drawio`

What was decided:

1. Split responsibilities clearly:
  - Frontend UI/UX and API gateway through Nginx proxy.
  - Backend for auth, interview logic, scoring, recommendations.
  - PostgreSQL for persistence.
2. Host app and platform services on the same small cluster for course project constraints.
3. Keep data-plane workloads on worker whenever possible.

Why this phase mattered:

1. Reduced ambiguity in later Terraform, Ansible, and manifest design.
2. Clarified service names and network assumptions early.

## Phase 2 - Containerization

Artifacts:

1. `backend/Dockerfile`
2. `frontend/Dockerfile`
3. `frontend/nginx.conf`
4. `docker-compose.yml`

What was implemented:

1. Backend image:
  - Python runtime with required dependencies.
  - FastAPI served by uvicorn.
2. Frontend image:
  - Build stage using Vite.
  - Runtime stage with Nginx.
  - `/api/` reverse proxy to backend service.
3. Local integration via Docker Compose for rapid validation.

Incidents and fixes:

1. Production frontend called localhost:
  - Root cause: Vite build arg default baked `http://localhost:8000` into static JS.
  - Fix: default `VITE_API_URL=/api` and keep Nginx API proxy enabled.

## Phase 3 - Infrastructure as Code (Terraform)

Artifacts:

1. `infra/terraform/main.tf`
2. `infra/terraform/variables.tf`
3. `infra/terraform/outputs.tf`
4. `infra/terraform/terraform.tfvars.example`

What was provisioned:

1. Two EC2 nodes (master + worker).
2. Security group ingress for:
  - SSH (22)
  - K3s API (6443)
  - Frontend NodePort (30080)
  - Other required app ports.

Incidents and fixes:

1. Large files accidentally entered Git history (`.terraform` provider binary and tfstate files).
  - Root cause: generated Terraform local artifacts were tracked.
  - Fixes:
    - Expanded `.gitignore` to exclude Terraform local state/providers.
    - Rewrote local branch history and force-pushed cleaned commits.

## Phase 4 - Cluster Provisioning (Ansible + K3s)

Artifacts:

1. `infra/ansible/install-k3s.yml`
2. `infra/ansible/inventory.ini`
3. `infra/ansible/ansible.cfg`

What was automated:

1. Node preparation (packages, swap disable, sysctl).
2. K3s server install on master.
3. Token retrieval and worker join.
4. Readiness checks from master.

Critical stabilization decision:

1. Added control-plane taint on master:
  - `node-role.kubernetes.io/control-plane=true:NoSchedule`
2. Reason:
  - On small instances, app + DB scheduling on master caused severe instability.

## Phase 5 - Kubernetes App Deployment

Artifacts:

1. `infra/k8s/00-namespace.yaml`
2. `infra/k8s/01-db-secret.yaml`
3. `infra/k8s/02-db-pvc.yaml`
4. `infra/k8s/03-db-service.yaml`
5. `infra/k8s/04-db-statefulset.yaml`
6. `infra/k8s/05-backend-deployment.yaml`
7. `infra/k8s/06-backend-service.yaml`
8. `infra/k8s/07-frontend-deployment.yaml`
9. `infra/k8s/08-frontend-service.yaml`
10. `infra/k8s/apply.ps1`
11. `infra/k8s/apply.sh`
12. `infra/k8s/apply-remote.ps1`

Operational incidents resolved:

1. Frontend could not call backend (`ERR_CONNECTION_REFUSED`):
  - Root cause: frontend bundle pointed to localhost.
  - Fix: rebuild and redeploy frontend with `/api` target.

2. Categories endpoint returned 503 and UI crashed:
  - Root causes:
    - Backend startup data files not loaded in container path.
    - Frontend assumed `top_categories` always exists and called `Object.keys` on undefined.
  - Fixes:
    - Backend: corrected base data path and bundled required CSV files in image.
    - Backend: categories endpoint guard changed to require questions data only.
    - Frontend: added safe parsing, payload checks, and retry logic for transient 503.

3. Register endpoint 422 confusion:
  - Root cause: frontend password min length differed from backend validation.
  - Fixes:
    - Frontend validation aligned with backend rules.
    - Better 422 error parsing and user-facing messages.

4. Backend rollout hangs on resource-constrained worker:
  - Root cause: rollout surge behavior tried running old + new pods concurrently.
  - Fix: conservative rolling strategy in backend deployment (`maxSurge: 0`, `maxUnavailable: 1`).

## Phase 6 - CI/CD Pipeline (Build + Deploy)

Workflow:

1. `.github/workflows/phase6-cicd-k3s.yml`

Trigger model:

1. Push to `devOps` branch (selected paths).
2. Manual dispatch supported for controlled release.

Quality gate model:

1. Deployment is blocked unless backend tests pass.
2. Deployment is blocked unless frontend tests pass.
3. Build and push job starts only after both test jobs are green.

Pipeline stages in detail:

1. Backend test job (`pytest`):
  - Python 3.10 setup.
  - Install `backend/requirements-test.txt`.
  - Run `python -m pytest -q`.
2. Frontend test job (`npm test`):
  - Node 20 setup.
  - Install dependencies with `npm ci`.
  - Run `npm test` (Vitest).
3. Checkout repository.
4. Setup Docker Buildx.
5. Authenticate to Docker Hub.
6. Build and push backend image:
  - `<DOCKERHUB_USERNAME>/svi-backend:latest`
  - `<DOCKERHUB_USERNAME>/svi-backend:<github.sha>`
7. Build and push frontend image:
  - `<DOCKERHUB_USERNAME>/svi-frontend:latest`
  - `<DOCKERHUB_USERNAME>/svi-frontend:<github.sha>`
8. SSH to K3s master and deploy:
  - `kubectl set image` for backend and frontend deployments.
  - `kubectl rollout status` checks.
  - Automatic fallback recreate if rollout times out on constrained capacity.
  - Pod listing for visibility.

Required GitHub secrets:

1. `DOCKERHUB_USERNAME`
2. `DOCKERHUB_TOKEN`
3. `K3S_HOST`
4. `K3S_SSH_USER`
5. `K3S_SSH_PRIVATE_KEY`
6. `K3S_SSH_PORT` (optional)

Release traceability model:

1. `latest` for convenience.
2. Commit SHA tags for deterministic rollback and auditability.

Test assets added to the repository:

1. Backend:
  - `backend/pytest.ini`
  - `backend/requirements-test.txt`
  - `backend/tests/conftest.py`
  - `backend/tests/test_initialization.py`
  - `backend/tests/test_validation.py`
  - `backend/tests/test_api_integration.py`
2. Frontend:
  - `frontend/vite.config.js` (Vitest config)
  - `frontend/src/test/setup.js`
  - `frontend/src/confetti.test.js`
  - `frontend/src/App.integration.test.jsx`
  - `frontend/package.json` test script (`npm test`)

## Phase 7 - Rollback Workflow

Workflow:

1. `.github/workflows/phase7-rollback-k3s.yml`

Execution model:

1. Manual run only (`workflow_dispatch`).
2. Inputs:
  - `backend_tag`
  - `frontend_tag`

Rollback stages:

1. Start SSH agent with repository private key secret.
2. SSH into K3s master.
3. Set deployment image tags to specified values.
4. Wait for rollout status to complete.
5. Print currently active deployment images.

Operational strategy:

1. Keep a list of known-good SHA tags from successful Phase 6 runs.
2. Roll back to exact SHA tags when a release is faulty.

## 5. End-to-End Delivery Pipeline

Developer to production flow:

1. Developer pushes code to `devOps`.
2. GitHub Actions builds backend/frontend images.
3. Images are pushed to Docker Hub with `latest` and SHA tags.
4. Workflow SSHes to K3s master and updates deployment images.
5. Kubernetes performs rollout and health stabilization.
6. Team validates app and API behavior.
7. If failure occurs, rollback workflow redeploys previous known-good tags.

## 6. Operational Playbooks

## 6.1 Post-Deploy Validation

Run after each deployment:

1. Open frontend:
  - `http://<MASTER_PUBLIC_IP>:30080`
2. Verify health endpoint:
  - `http://<MASTER_PUBLIC_IP>:30080/api/health`
3. Verify categories endpoint:
  - `http://<MASTER_PUBLIC_IP>:30080/api/categories`
4. Verify active deployed image tags:

```bash
kubectl -n smart-interviewer get deploy backend frontend -o=jsonpath='{range .items[*]}{.metadata.name}{" => "}{.spec.template.spec.containers[0].image}{"\n"}{end}'
```

## 6.2 Pre-Deploy Validation (Local)

Before pushing to `devOps`, run locally:

1. Backend tests:

```bash
cd backend
python -m pytest -q
```

2. Frontend tests:

```bash
cd frontend
npm test
```

Expected baseline:

1. Backend: all tests passed (initialization, validation, integration).
2. Frontend: all tests passed (unit and integration-style).

## 6.3 Incident Response Checklist

If app is down or degraded:

1. Check frontend and backend rollout status.
2. Inspect pod states (`Pending`, `CrashLoopBackOff`, `ImagePullBackOff`).
3. Inspect backend logs for data/model startup issues.
4. Validate DB pod and PVC readiness.
5. If release is faulty, execute Phase 7 rollback to known-good SHA tags.

## 6.4 Git Hygiene and Artifact Safety

Rules:

1. Never commit:
  - `infra/terraform/.terraform/`
  - `infra/terraform/terraform.tfstate*`
  - local secrets files
2. Keep `.gitignore` current.
3. If large binary enters history, rewrite local branch before push.

## 7. Known Constraints and Tradeoffs

Current constraints:

1. Small EC2 shape (`t3.micro`) limits simultaneous rollout capacity.
2. Single worker topology prioritizes cost over high availability.
3. Rollback is manual trigger (intentionally explicit for control).

Tradeoffs accepted:

1. Cost-efficient project topology over multi-node HA.
2. Operational simplicity over advanced progressive delivery.

## 8. Lessons Learned

Major lessons from real incidents:

1. Control-plane isolation is non-negotiable on tiny clusters.
2. Frontend production API target must never rely on localhost assumptions.
3. Frontend must be resilient to transient backend readiness states.
4. Validation rules should be aligned backend and frontend to avoid user confusion.
5. CI/CD without rollback is incomplete and operationally risky.
6. Terraform local artifacts in Git can break delivery pipelines and repository integrity.

## 9. Current Platform Status

As of current state:

1. Infrastructure: provisioned and reachable.
2. K3s cluster: stable and healthy.
3. Application: accessible through NodePort on master public IP.
4. CI/CD: automated build and deploy active.
5. Rollback: dedicated workflow available and ready for use.

## 10. Next Improvement Opportunities

Recommended next upgrades:

1. Add staging environment and promote-to-production workflow.
2. Add smoke tests in CI before deploy step.
3. Add environment protection/approval gates in GitHub Actions.
4. Add alerting dashboards (Prometheus/Grafana or cloud-native monitoring).
5. Add automated database backup and restore drill runbook.

