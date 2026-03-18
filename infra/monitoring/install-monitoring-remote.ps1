param(
    [string]$MasterIp,
    [string]$SshKeyPath = "C:\Users\HP ZBOOK\.ssh\svi_key",
    [string]$SshUser = "ubuntu",
    [string]$MonitoringNamespace = "monitoring"
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($MasterIp)) {
    $terraformDir = Join-Path $PSScriptRoot "..\terraform"
    if (Test-Path $terraformDir) {
        try {
            Push-Location $terraformDir
            $masterOutput = terraform output -raw master_public_ip
            $terraformExit = $LASTEXITCODE
            Pop-Location

            if ($terraformExit -ne 0) {
                throw "terraform output failed with exit code $terraformExit"
            }

            $MasterIp = $masterOutput.Trim()
            if ([string]::IsNullOrWhiteSpace($MasterIp)) {
                throw "Empty Terraform output for master_public_ip"
            }
            Write-Host "Resolved MasterIp from Terraform output: $MasterIp"
        }
        catch {
            throw "MasterIp not provided and Terraform output lookup failed: $($_.Exception.Message)"
        }
    }
    else {
        throw "MasterIp not provided and terraform directory not found at $terraformDir"
    }
}

$sshOptions = @(
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "ConnectTimeout=20",
    "-o", "ServerAliveInterval=10",
    "-o", "ServerAliveCountMax=4"
)

$remoteDir = "/tmp/svi-monitoring"
$createdRemoteDir = $false
for ($attempt = 1; $attempt -le 5; $attempt++) {
    ssh @sshOptions -i $SshKeyPath "$SshUser@$MasterIp" "mkdir -p $remoteDir"
    if ($LASTEXITCODE -eq 0) {
        $createdRemoteDir = $true
        break
    }

    Write-Host "SSH attempt $attempt failed while creating $remoteDir. Retrying in 10s ..."
    Start-Sleep -Seconds 10
}

if (-not $createdRemoteDir) {
    throw "Failed to create remote directory $remoteDir"
}

$filesToCopy = @(
    "prometheus-values.yaml",
    "grafana-values.yaml"
)

foreach ($file in $filesToCopy) {
    $localPath = Join-Path $PSScriptRoot $file
    Write-Host "Copying $localPath to $MasterIp ..."

    $copied = $false
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        scp @sshOptions -i $SshKeyPath $localPath "$SshUser@$MasterIp`:$remoteDir/$file"
        if ($LASTEXITCODE -eq 0) {
            $copied = $true
            break
        }

        Write-Host "SCP attempt $attempt failed for $file. Retrying in 10s ..."
        Start-Sleep -Seconds 10
    }

    if (-not $copied) {
        throw "SCP failed for $file"
    }
}

$remoteCommands = @(
    'set -eu',
    'if ! command -v helm >/dev/null 2>&1; then curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash; fi',
    'if [ ! -f /swapfile ]; then sudo fallocate -l 4G /swapfile; fi',
    'sudo chmod 600 /swapfile',
    'sudo mkswap /swapfile >/dev/null 2>&1 || true',
    'sudo swapon /swapfile || true',
    'grep -q "^/swapfile " /etc/fstab || echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab >/dev/null',
    'free -h',
    'sudo test -f /etc/rancher/k3s/k3s.yaml',
    'sudo systemctl is-active --quiet k3s || sudo systemctl restart k3s',
    'api_ok=0; for i in 1 2 3 4 5 6 7 8 9 10 11 12; do sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl get --raw=/readyz >/dev/null 2>&1 && api_ok=1 && break; echo k3s API not ready attempt $i, waiting 10s...; sudo systemctl is-active --quiet k3s || sudo systemctl restart k3s; sleep 10; done; test $api_ok -eq 1',
    'sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl version',
    ("sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl get ns {0} >/dev/null 2>&1 || sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl create namespace {0}" -f $MonitoringNamespace),
    'sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm repo add prometheus-community https://prometheus-community.github.io/helm-charts',
    'sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm repo add grafana https://grafana.github.io/helm-charts',
    'sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm repo update',
    ("sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm uninstall monitoring --namespace {0} >/dev/null 2>&1 || true" -f $MonitoringNamespace),
    'sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm uninstall postgres-exporter --namespace smart-interviewer >/dev/null 2>&1 || true',
    ('prom_ok=0; for i in 1 2 3; do sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm upgrade --install prometheus prometheus-community/prometheus --namespace {0} --values {1}/prometheus-values.yaml --wait --timeout 12m && prom_ok=1 && break; echo prometheus install attempt $i failed, retrying in 25s...; sleep 25; done; test $prom_ok -eq 1' -f $MonitoringNamespace, $remoteDir),
    ('graf_ok=0; for i in 1 2 3; do sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm upgrade --install grafana grafana/grafana --namespace {0} --values {1}/grafana-values.yaml --wait --timeout 8m && graf_ok=1 && break; echo grafana install attempt $i failed, retrying in 20s...; sleep 20; done; test $graf_ok -eq 1' -f $MonitoringNamespace, $remoteDir),
    ("sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl -n {0} get pods,svc" -f $MonitoringNamespace)
)

$remoteScript = $remoteCommands -join "; "
$executedRemoteScript = $false
for ($attempt = 1; $attempt -le 5; $attempt++) {
    ssh @sshOptions -i $SshKeyPath "$SshUser@$MasterIp" "bash -lc '$remoteScript'"
    if ($LASTEXITCODE -eq 0) {
        $executedRemoteScript = $true
        break
    }

    Write-Host "Remote install attempt $attempt failed. Retrying in 20s ..."
    Start-Sleep -Seconds 20
}

if (-not $executedRemoteScript) {
    throw "Remote Helm install failed"
}

Write-Host "Monitoring stack installed successfully."
Write-Host "Grafana URL: http://$MasterIp:30300"
Write-Host "Grafana user: admin"
Write-Host "Grafana password: admin123"
