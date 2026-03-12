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

The push refers to repository [docker.io/aymenexe/svi-frontend]
61ca4f733c80: Pushed
82ad9f22b70f: Pushed
f18232174bc9: Mounted from aymenexe/firstapp
197eb75867ef: Pushed
b464cfdf2a63: Pushed
d7e507024086: Pushed
81bd8ed7ec67: Pushed
4f245ffb6b52: Pushed
34a64644b756: Pushed
a5f50e7551e6: Pushed
95cf6bca842d: Pushed
39c2ddfd6010: Pushed
latest: digest: sha256:a65d54d3017403bcbe6558c7a3fc914f7512322b5bf0afa4f1b8d7e65376207f size: 856


The push refers to repository [docker.io/aymenexe/svi-backend]
4d1e02f91db8: Pushed
aecf3e6b3e04: Pushed
f937e6e71171: Pushed
ce7afba89736: Pushed
206356c42440: Pushed
44df7c9b0118: Pushed
623df85cc3f0: Pushed
98e22c324dcf: Pushed
7fe6b2798913: Pushed
f875d262a812: Pushed
7187a497fe0b: Pushed
latest: digest: sha256:fd61dd406125aaa64e7c1a4c6f7ad226ac6a854d1e3a1db335894579c94fc32b size: 856
PS D:\Jira_Project> 
---

## Quick Reference — Credentials to Keep Safe

| Secret | Where used | How to generate |
|--------|-----------|----------------|
| `SECRET_KEY` | JWT signing | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `POSTGRES_PASSWORD` | DB auth | Choose a strong password (16+ chars) |
| Docker Hub password | Image push/pull | Set in Docker Hub account settings |
| AWS Access Key + Secret | Terraform (Phase 3) | IAM → Create access key |
| SSH key pair | EC2 access / Ansible | `ssh-keygen -t ed25519 -f ~/.ssh/svi_key` |

---

*Phases 3–7 manual steps will be added here as each phase is completed.*
