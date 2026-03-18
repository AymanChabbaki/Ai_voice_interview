# Manual Steps to Complete Each Phase

> Everything in this file is what **you** must do by hand.
> Code files, configs, and manifests are already generated — this is the human-in-the-loop checklist.

---

## Phase 1 — Architecture Diagram ✅

### What was generated
`docs/architecture.drawio`

### What you must do manually

- [ ] **Open the diagram**
  1. Go to [app.diagrams.net](https://app.diagrams.net)
  2. Click **File → Open from → Device**
  3. Select `docs/architecture.drawio`

- [ ] **Review and adjust**
  - Confirm the two EC2 nodes match your actual AWS region / AZ layout
  - Confirm service names match what you plan to use in Kubernetes (e.g. `db-service`, `backend-service`)
  - Add your team name / project title in the diagram title bar if required for submission

- [ ] **Export for submission**
  - **File → Export as → PNG** (300 dpi, fit page)
  - Save as `docs/architecture.png`
  - **File → Export as → PDF** if your professor requires it
  - Commit both files to Git

---

## Phase 2 — Docker ✅

### What was generated
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `docker-compose.yml`
- `.dockerignore`

### What you must do manually

#### 2.1 — Install Docker Desktop (if not installed)
- [ ] Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
- [ ] Enable **WSL 2 backend** on Windows during install
- [ ] Verify: open PowerShell and run:
  ```powershell
  docker --version
  docker compose version
  ```

#### 2.2 — Create your local `.env` file
- [ ] In the project root, duplicate the backend example:
  ```powershell
  Copy-Item backend\.env.example backend\.env
  ```
- [ ] Open `backend\.env` and fill in **both required values**:
  ```
  SECRET_KEY=<paste output of: python -c "import secrets; print(secrets.token_hex(32))">
  DATABASE_URL=postgresql://svi:yourpassword@db:5432/smart_interviewer
  ```
- [ ] Create a **root-level `.env`** for docker-compose secrets:
  ```powershell
  New-Item .env
  ```
  Add these lines:
  ```
  POSTGRES_USER=svi
  POSTGRES_PASSWORD=yourpassword
  POSTGRES_DB=smart_interviewer
  SECRET_KEY=<same value as above>
  ```
  > ⚠️ Never commit either `.env` file. Both are already in `.gitignore`.

#### 2.3 — Build and start the stack
- [ ] From the project root:
  ```powershell
  docker compose up --build
  ```
- [ ] Wait for all three services to show `healthy` / `started`:
  - `db` → `database system is ready to accept connections`
  - `backend` → `Uvicorn running on http://0.0.0.0:8000`
  - `frontend` → nginx starts silently

#### 2.4 — Smoke test
- [ ] Open **http://localhost** — React app should load
- [ ] Open **http://localhost:8000/health** — should return `{"status":"healthy",...}`
- [ ] Open **http://localhost:8000/docs** — FastAPI Swagger UI should load
- [ ] Register a test user via the UI and confirm it persists after `docker compose restart backend`

#### 2.5 — Tag and push images to a registry
> Required before Kubernetes can pull them.

- [ ] Create a free account on [Docker Hub](https://hub.docker.com) (or use AWS ECR / GitLab Registry)
- [ ] Log in:
  ```powershell
  docker login
  ```
- [ ] Tag and push the backend image:
  ```powershell
  docker tag jira_project-backend <your-dockerhub-username>/svi-backend:latest
  docker push <your-dockerhub-username>/svi-backend:latest
  ```
- [ ] Tag and push the frontend image:
  ```powershell
  docker tag jira_project-frontend <your-dockerhub-username>/svi-frontend:latest
  docker push <your-dockerhub-username>/svi-frontend:latest
  ```
- [ ] Note down the full image names — you will paste them into the Kubernetes `deployment.yaml` manifests in Phase 5.

---

## Phase 3 — Terraform (2x t3.micro) ✅

### What was generated
- `infra/terraform/main.tf`
- `infra/terraform/variables.tf`
- `infra/terraform/outputs.tf`
- `infra/terraform/terraform.tfvars.example`

### What you must do manually

#### 3.1 — Install Terraform (if missing)
- [ ] Verify Terraform is installed:
  ```powershell
  terraform version
  ```
- [ ] If command is not found, install Terraform and reopen PowerShell.

#### 3.2 — Configure AWS credentials
- [ ] Install/configure AWS CLI and set credentials:
  ```powershell
  aws configure
  ```
- [ ] Confirm account access:
  ```powershell
  aws sts get-caller-identity
  ```

#### 3.3 — Prepare terraform variables
- [ ] Go to terraform folder:
  ```powershell
  cd infra\terraform
  ```
- [ ] Create local tfvars file:
  ```powershell
  Copy-Item terraform.tfvars.example terraform.tfvars
  ```
- [ ] Edit `terraform.tfvars` and set:
  - `key_name` (existing AWS keypair) **or** `public_key_path` (local `.pub` key)
  - `allowed_ssh_cidr` = your public IP CIDR (recommended) or `0.0.0.0/0`
  - `aws_region` if different from default

#### 3.4 — Create infrastructure
- [ ] Initialize Terraform:
  ```powershell
  terraform init
  ```
- [ ] Check plan:
  ```powershell
  terraform plan
  ```
- [ ] Apply:
  ```powershell
  terraform apply -auto-approve
  ```

#### 3.5 — Save outputs for Ansible
- [ ] Export both IPs (or copy from output):
  ```powershell
  terraform output master_public_ip
  terraform output worker_public_ip
  ```
- [ ] Keep these IPs ready for Phase 4 inventory.

---

## Phase 4 — Ansible (K3s install) ✅

### What was generated
- `infra/ansible/ansible.cfg`
- `infra/ansible/inventory.ini.example`
- `infra/ansible/install-k3s.yml`

### What you must do manually

#### 4.1 — Install Ansible (control machine)
- [ ] Verify Ansible:
  ```powershell
  ansible --version
  ```
- [ ] If missing, install Ansible (prefer WSL Ubuntu for Windows users).

#### 4.2 — Verify SSH access to EC2 nodes
- [ ] Test SSH to master and worker using your keypair:
  ```powershell
  ssh -i <path-to-key.pem> ubuntu@<MASTER_PUBLIC_IP>
  ssh -i <path-to-key.pem> ubuntu@<WORKER_PUBLIC_IP>
  ```
- [ ] If SSH fails, fix Security Group rule for port 22 and keypair path/permissions.

#### 4.3 — Build inventory from Terraform outputs
- [ ] Go to ansible folder:
  ```powershell
  cd ..\ansible
  ```
- [ ] Copy inventory template:
  ```powershell
  Copy-Item inventory.ini.example inventory.ini
  ```
- [ ] Replace placeholders in `inventory.ini` with actual public IPs from Terraform.

#### 4.4 — Run K3s installation playbook
- [ ] Run playbook (with your SSH key):
  ```powershell
  ansible-playbook -i inventory.ini install-k3s.yml --private-key <path-to-key.pem>
  ```

#### 4.5 — Validate cluster after install
- [ ] SSH into master and check nodes:
  ```powershell
  ssh -i <path-to-key.pem> ubuntu@<MASTER_PUBLIC_IP>
  sudo kubectl get nodes -o wide
  ```
- [ ] Expect both nodes to be `Ready`.

---

## Phase 5 — Kubernetes manifests ✅

### What was generated
- `infra/k8s/00-namespace.yaml`
- `infra/k8s/01-db-secret.yaml`
- `infra/k8s/02-db-pvc.yaml`
- `infra/k8s/03-db-service.yaml`
- `infra/k8s/04-db-statefulset.yaml`
- `infra/k8s/05-backend-deployment.yaml`
- `infra/k8s/06-backend-service.yaml`
- `infra/k8s/07-frontend-deployment.yaml`
- `infra/k8s/08-frontend-service.yaml`
- `infra/k8s/apply.sh`
- `infra/k8s/apply.ps1`

### What you must do manually

#### 5.1 — Rebuild and push frontend image (required)
> The frontend was updated to call `/api` through nginx proxy, so you must rebuild/push it before deploying to K8s.

- [ ] Build and push frontend:
  ```powershell
  cd frontend
  docker build -t <your-dockerhub-username>/svi-frontend:latest .
  docker push <your-dockerhub-username>/svi-frontend:latest
  ```

#### 5.2 — Ensure backend image exists in registry
- [ ] If needed, rebuild/push backend image:
  ```powershell
  cd ..\backend
  docker build -t <your-dockerhub-username>/svi-backend:latest .
  docker push <your-dockerhub-username>/svi-backend:latest
  ```

#### 5.3 — Set Kubernetes image names
- [ ] Open these files and set your Docker Hub namespace if different:
  - `infra/k8s/05-backend-deployment.yaml`
  - `infra/k8s/07-frontend-deployment.yaml`

#### 5.4 — Set production secrets
- [ ] Edit `infra/k8s/01-db-secret.yaml` and replace:
  - `POSTGRES_PASSWORD`
  - `DATABASE_URL` password segment
  - `SECRET_KEY`

#### 5.5 — Apply manifests to cluster
- [ ] Copy manifests to your master host (or run from a machine with kubeconfig context to your K3s cluster).
- [ ] Apply in order:
  ```powershell
  cd infra/k8s
  .\apply.ps1
  ```
  Linux/macOS alternative:
  ```bash
  cd infra/k8s
  bash apply.sh
  ```

#### 5.6 — Verify deployment
- [ ] Check pods/services/PVC:
  ```bash
  kubectl -n smart-interviewer get pods,svc,pvc
  ```
- [ ] Access app via NodePort:
  - `http://<MASTER_PUBLIC_IP>:30080`

#### 5.7 — Basic smoke test
- [ ] In browser, open frontend NodePort URL.
- [ ] Verify backend health through proxied API:
  - `http://<MASTER_PUBLIC_IP>:30080/api/health`
- [ ] Verify categories load in UI (frontend should no longer call `localhost:8000`).

---

## Phase 6 — CI/CD (GitHub Actions) ✅

### What was generated
- `.github/workflows/phase6-cicd-k3s.yml`

### What you must do manually

#### 6.1 — Push your repository to GitHub
- [ ] Ensure this project is hosted in a GitHub repository with Actions enabled.
- [ ] Push your latest branch to `main`.

#### 6.2 — Add required GitHub repository secrets
- [ ] Open **GitHub Repo → Settings → Secrets and variables → Actions**.
- [ ] Create these secrets:
  - `DOCKERHUB_USERNAME` = your Docker Hub username
  - `DOCKERHUB_TOKEN` = Docker Hub access token (not password)
  - `K3S_HOST` = master public IP (e.g. `3.231.151.216`)
  - `K3S_SSH_USER` = `ubuntu`
  - `K3S_SSH_PRIVATE_KEY` = private SSH key content used for EC2 access
  - `K3S_SSH_PORT` = `22` (optional; defaults to 22)

#### 6.3 — First pipeline run
- [ ] Trigger workflow manually from **Actions → Phase 6 - CI/CD to K3s → Run workflow**.
- [ ] Confirm both jobs pass:
  - `Build and Push Images`
  - `Deploy to K3s`

#### 6.4 — Verify deployment result
- [ ] Open app URL:
  - `http://<MASTER_PUBLIC_IP>:30080`
- [ ] Verify API health:
  - `http://<MASTER_PUBLIC_IP>:30080/api/health`
- [ ] Verify new image tags are set on cluster:
  ```bash
  kubectl -n smart-interviewer get deploy backend frontend -o=jsonpath='{range .items[*]}{.metadata.name}{" => "}{.spec.template.spec.containers[0].image}{"\n"}{end}'
  ```

#### 6.5 — Ongoing usage
- [ ] Any push to `main` touching `backend/**`, `frontend/**`, `infra/k8s/**`, or workflow file auto-triggers build + deploy.
- [ ] Use manual dispatch for controlled releases when needed.

---

## Quick Reference — Credentials to Keep Safe

| Secret | Where used | How to generate |
|--------|-----------|----------------|
| `SECRET_KEY` | JWT signing | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `POSTGRES_PASSWORD` | DB auth | Choose a strong password (16+ chars) |
| Docker Hub password | Image push/pull | Set in Docker Hub account settings |
| AWS Access Key + Secret | Terraform (Phase 3) | IAM → Create access key |
| SSH key pair | EC2 access / Ansible | `ssh-keygen -t ed25519 -f ~/.ssh/svi_key` |
