# Azure Kubernetes Setup (Terraform + Ansible)

This setup provisions your requested architecture on Azure:

- 1 Kubernetes master node (also external load balancer)
- 2 Kubernetes worker nodes
- Frontend and backend scheduled on worker nodes
- PostgreSQL pinned to a single dedicated worker node

## 1. Prerequisites

Install on your local machine:

- Terraform >= 1.6
- Ansible >= 2.15
- Azure CLI
- SSH key pair (`~/.ssh/id_rsa` and `~/.ssh/id_rsa.pub`)

Login to Azure:

```powershell
az login
az account show
```

## 2. Provision Infrastructure with Terraform

```powershell
cd infra/terraform
Copy-Item terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set at least:

- `subscription_id`
- `ssh_public_key_path`
- `admin_allowed_cidr` (set this to your public IP/CIDR in production)

Apply:

```powershell
terraform init
terraform plan
terraform apply -auto-approve
```

Get outputs:

```powershell
terraform output
```

## 3. Generate Ansible Inventory

From `infra/terraform`:

```powershell
./generate_inventory.ps1 -AnsibleUser azureuser -PrivateKeyPath ~/.ssh/id_rsa
```

This updates `infra/ansible/inventory/hosts.ini` with master/worker IPs.

## 4. Bootstrap Cluster + Deploy App with Ansible

Go to Ansible folder:

```powershell
cd ../ansible
```

Optional overrides for secrets/database credentials:

- `app_secret_key`
- `postgres_user`
- `postgres_password`
- `postgres_db`

Run playbook:

```powershell
ansible-playbook playbooks/site.yml -e "app_secret_key=CHANGE_THIS_SECRET"
```

What this playbook does:

- Installs containerd + kubeadm/kubelet/kubectl on all nodes
- Initializes Kubernetes master and joins workers
- Labels workers for workload scheduling
- Labels the first worker as `workload=database`
- Deploys Azure-specific manifests from `k8s/azure`
- Installs and configures HAProxy on master

## 5. Access the Application

The master node public IP is your entry point.

- Frontend: `http://MASTER_PUBLIC_IP/`
- Backend API via HAProxy path rule: `http://MASTER_PUBLIC_IP/api/...`

HAProxy routing:

- `/api` -> backend NodePort (`30800`) across both workers
- everything else -> frontend NodePort (`30080`) across both workers

## 6. Files Added

- `infra/terraform/*`: Azure VM/network provisioning
- `infra/terraform/generate_inventory.ps1`: inventory generator from Terraform outputs
- `infra/ansible/playbooks/site.yml`: cluster bootstrap + app deploy
- `infra/ansible/templates/haproxy.cfg.j2`: master load balancer config
- `infra/ansible/templates/ai-interview-secrets.yaml.j2`: secrets templating
- `k8s/azure/*`: worker-aware manifests

## 7. Notes and Limits

- This is a single-master cluster (no HA control plane).
- PostgreSQL on one worker uses a PVC, but storage is tied to node/cluster lifetime.
- For production, use:
  - Azure Disk-backed `StorageClass`
  - managed database (Azure Database for PostgreSQL)
  - HTTPS termination and certificates (for example, cert-manager + ingress)
  - locked-down NSG source ranges
