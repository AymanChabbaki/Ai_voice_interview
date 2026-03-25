# Complete DevOps Pipeline Strategy

This document details the entire end-to-end DevOps pipeline for the Smart Voice Interviewer project, covering all phases from infrastructure provisioning to application deployment, continuous integration (CI), continuous delivery (CD), and automated rollbacks.

---

## Phase 1: Architecture Design
The foundation of the pipeline begins with a clear architectural split between the components:
- **Frontend**: A React application utilizing Vite, served behind an Nginx reverse proxy routing API requests seamlessly.
- **Backend**: A Python FastAPI service handling interview logic, authentication, and semantic scoring via SBERT.
- **Database**: A PostgreSQL database persisting user and application state.
- **Infrastructure**: A two-node Kubernetes cluster (K3s) on AWS EC2 `t3.micro` instances (Master + Worker), communicating over an internal network.

---

## Phase 2: Containerization (Docker)
To enforce environment parity, the application is strictly containerized.
- **Backend Dockerfile**: Installs Python 3.10, PyTorch, and FastAPI dependencies. Uses Uvicorn to serve the API.
- **Frontend Dockerfile**: Multi-stage build compiling the Vite bundle and serving static files via an Nginx alpine image configured to proxy `/api/` traffic to the backend service.
- **Local Validation**: A `docker-compose.yml` file allows engineers to spin up the entire isolated stack locally to iterate rapidly prior to CI/CD involvement.

---

## Phase 3: Infrastructure as Code (Terraform)
All infrastructure is declared dynamically through code to ensure repeatable state provisioning instead of manual clicking in the AWS Console.
- **Tools Used**: HashiCorp Terraform.
- **Resources Managed**: Two AWS EC2 `t3.micro` instances within the free tier.
- **Security Groups**: Granularly controls ingress for SSH (Port 22), K3s API (Port 6443), and the NodePort service exposing the application frontend (Port 30080).

---

## Phase 4: Cluster Provisioning (Ansible & K3s)
Following EC2 provisioning, the pipeline bootstraps the orchestration layer automatically.
- **Configuration Management Tools**: Ansible playbooks (`install-k3s.yml`, `inventory.ini`).
- **Cluster Deployment strategy**: 
  - Master Node initializes the primary control plane server for K3s.
  - Generates cluster joining tokens explicitly retrieved by Ansible.
  - Worker Node joins via token over internal networking.
  - Applies a strict control-plane taint (`node-role.kubernetes.io/control-plane=true:NoSchedule`) on the Master node to protect its stability from memory-hungry application workloads.

---

## Phase 5: Kubernetes Manifest Application (K8s)
With the cluster alive, declarative Kubernetes `.yaml` manifests translate the logical architecture into living deployments.
- **Storage Layer**: Creates a standard PersistentVolume (AWS EBS Volume) linking dynamically to a PersistentVolumeClaim (`db-pvc.yaml`) for resilient database storage.
- **Stateful Workloads**: Deploys the PostgreSQL container using a `StatefulSet` attached to the PVC, and exposing the cluster-internal database service.
- **Stateless Workloads**: Deploys the Backend API (`05-backend-deployment.yaml`) scaling strictly via `RollingUpdate` overrides tailored for micro-instances (`maxSurge=0`, `maxUnavailable=1`). Deploys the Frontend Web server to route ingress internet traffic from `NodePort`.
- **Secrets Management**: Connects pods explicitly through mapped `envFrom` declarations linked directly to unified opaque secrets (`01-db-secret.yaml`).

---

## Phase 6: Continuous Integration & Delivery (GitHub Actions)
The operational lifecycle transitions to automated CI/CD upon code commits to the `devOps` branch, captured in `.github/workflows/phase6-cicd-k3s.yml`.

### 1: Quality Gates (Pre-Build Validation)
- Parallel remote runners spin up to independently validate that no broken code transitions backward along the pipeline.
- Executes `pytest` against Python testing matrices on the backend.
- Executes `npm test` enforcing Vite test components dynamically against the React frontend.

### 2: Build & Push
- Only after both gates pass successfully, `docker/build-push-action@v6` triggers.
- Both Frontend and Backend containers are built from their respective module definitions.
- The containers are uploaded directly to the authorized **Docker Hub Registry**.
- Traceability is guaranteed natively by double-tagging every image with explicitly both `latest` and a unique `${{ github.sha }}` hash value aligned to the commit tree.

### 3: Continuous Deployment to K3s 
- GitHub runner authorizes a secure `read-write` key injection sequence via SSH pointing to the EC2 Master IP address.
- Using native CLI patches, it initiates rolling patches updating the active `image:` tags across `deployment/frontend` and `deployment/backend`.
- **Resilience Engineering**: Explicit rollout observation rules strictly bound the maximum deployment window. If rolling updates choke via OOM limits on the micro-node bounds, it forcefully collapses to a recreate strategy terminating the older pods synchronously explicitly allowing the new pod memory footprints.

---

## Phase 7: Deterministic Rollbacks (GitHub Actions)
Because continuous delivery fundamentally embraces failure recovery, a separate explicit disaster recovery pipeline remains available.
- Resides manually inside `.github/workflows/phase7-rollback-k3s.yml` preventing accidental automation fires.
- Accepts distinct configuration parameters pointing squarely at pre-verified safe `<github.sha>` Docker tags.
- Initiates forced image-patching toward Kubernetes exactly matching the legacy configurations. Validating successful deployment rollout completions instantly afterward.
