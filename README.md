# Smart Voice Interviewer

Smart Voice Interviewer is an AI-powered mock interview platform.
It combines a React frontend, a FastAPI backend, semantic answer scoring, PostgreSQL persistence, and a Kubernetes deployment pipeline on AWS.

## What This Project Does

- Runs realistic interview sessions by topic and number of questions.
- Scores answers using semantic similarity (Sentence-BERT + cosine similarity).
- Tracks user progress, history, streaks, and profile data.
- Recommends learning resources after interviews.
- Deploys to a K3s cluster with CI/CD and rollback workflows.

## Architecture

- Frontend: React + Vite + Nginx
- Backend: FastAPI + JWT auth + rate limiting
- Database: PostgreSQL
- AI Layer: sentence-transformers (all-MiniLM-L6-v2)
- Infra: Terraform + Ansible + Kubernetes manifests
- Monitoring: Helm + Prometheus + Grafana
- Cloud: AWS EC2 (1 control-plane, 1 worker)
- CI/CD: GitHub Actions

Request flow:

1. Browser calls frontend on NodePort.
2. Frontend proxies `/api/*` via Nginx to backend service.
3. Backend validates/authenticates request.
4. Backend reads/writes PostgreSQL and runs AI scoring.
5. Response returns through frontend to user.

## Repository Structure

```text
backend/                FastAPI service, auth, scoring, DB logic
frontend/               React app and Nginx proxy config
infra/terraform/        AWS provisioning
infra/ansible/          K3s bootstrap and cluster setup
infra/k8s/              Namespace, DB, backend, frontend manifests
infra/monitoring/       Helm values and monitoring install script
docs/                   Manuals and supporting docs
.github/workflows/      CI/CD and rollback workflows
```

## Local Development

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker Desktop
- PostgreSQL (if running backend without Docker)

### Run With Docker Compose

From repo root:

```powershell
docker compose up --build
```

Then open:

- Frontend: http://localhost
- Backend health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Production Deployment Summary

The production environment is deployed on AWS and Kubernetes with the following approach:

1. Terraform provisions EC2 instances and security group rules.
2. Ansible installs K3s and joins worker to master.
3. Kubernetes manifests deploy DB, backend, frontend in namespace `smart-interviewer`.
4. Frontend is exposed via NodePort `30080`.

## Monitoring Stack (Helm)

Prometheus and Grafana are installed using lightweight Helm charts tuned for t3.micro.

Files:

- `infra/monitoring/prometheus-values.yaml`
- `infra/monitoring/grafana-values.yaml`
- `infra/monitoring/install-monitoring-remote.ps1`

Install from your local machine:

```powershell
cd infra/monitoring
./install-monitoring-remote.ps1 -MasterIp <MASTER_PUBLIC_IP>
```

Access:

- Grafana: `http://<MASTER_PUBLIC_IP>:30300`
- Default login: `admin / admin123`

What you get:

1. VM/Node CPU and memory dashboards from Prometheus node metrics.
2. Kubernetes workload metrics (pods, deployments, resource usage).
3. PostgreSQL exporter is deferred for now on t3.micro and can be enabled later.

## CI/CD

### Phase 6 Workflow

File: `.github/workflows/phase6-cicd-k3s.yml`

On push to `devOps` (selected paths), workflow:

1. Builds backend image.
2. Builds frontend image.
3. Pushes both to Docker Hub with `latest` and commit SHA tags.
4. SSHes to K3s master.
5. Updates deployment images using `kubectl set image`.
6. Waits for rollout status.

### Phase 7 Rollback Workflow

File: `.github/workflows/phase7-rollback-k3s.yml`

Manual workflow to roll back backend/frontend independently to any known image tag.

## Important Secrets

Configured in GitHub Actions secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `K3S_HOST`
- `K3S_SSH_USER`
- `K3S_SSH_PRIVATE_KEY`
- `K3S_SSH_PORT` (optional)

## Known Operational Notes

- The cluster is resource-constrained (t3.micro nodes), so rollout strategy matters.
- Backend deployment uses conservative rolling update settings to avoid scheduling deadlocks.
- Terraform local state and provider binaries must stay out of Git.

## Quick Troubleshooting

- Frontend calling localhost in production:
  - Ensure frontend image built with `VITE_API_URL=/api`.
- Categories endpoint 503:
  - Check backend data load and mounted/bundled CSV files.
- Register 422:
  - Backend enforces username/name/password validation; frontend now mirrors these rules.
- Push rejected by GitHub file size:
  - Remove `.terraform` provider binaries and rewrite local branch history before pushing.

## Documentation

- User/deployment checklist: `docs/MANUAL_STEPS.md`
- API documentation: `docs/API.md`
- DevOps phase walkthrough: `DEVOPS.md`

## License

For academic/project use. Add an explicit license file if required for public distribution.
