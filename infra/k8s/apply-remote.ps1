param(
    [string]$MasterIp,

    [string]$SshKeyPath = "C:\Users\HP ZBOOK\.ssh\svi_key",

    [string]$SshUser = "ubuntu"
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

$manifests = @(
    "00-namespace.yaml",
    "01-db-secret.yaml",
    "02-db-pvc.yaml",
    "03-db-service.yaml",
    "04-db-statefulset.yaml",
    "06-backend-service.yaml",
    "05-backend-deployment.yaml",
    "07-frontend-deployment.yaml",
    "08-frontend-service.yaml"
)

$sshOptions = @(
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "ConnectTimeout=12",
    "-o", "ServerAliveInterval=10",
    "-o", "ServerAliveCountMax=2"
)

$remoteDir = "/tmp/svi-k8s"
ssh @sshOptions -i $SshKeyPath "$SshUser@$MasterIp" "mkdir -p $remoteDir"
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create remote manifest directory $remoteDir"
}

foreach ($manifest in $manifests) {
    Write-Host "Applying $manifest on $MasterIp ..."
    $applied = $false

    for ($attempt = 1; $attempt -le 3; $attempt++) {
        scp @sshOptions -i $SshKeyPath $manifest "$SshUser@$MasterIp`:$remoteDir/$manifest"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "SCP attempt $attempt failed for $manifest. Retrying in 8s ..."
            Start-Sleep -Seconds 8
            continue
        }

        ssh @sshOptions -i $SshKeyPath "$SshUser@$MasterIp" "timeout 30s kubectl apply --request-timeout=20s --validate=false -f $remoteDir/$manifest"
        if ($LASTEXITCODE -eq 0) {
            $applied = $true
            break
        }

        Write-Host "Apply attempt $attempt failed for $manifest. Retrying in 8s ..."
        Start-Sleep -Seconds 8
    }

    if (-not $applied) {
        throw "Remote kubectl apply failed for $manifest after 3 attempts"
    }
}

Write-Host "All manifests applied remotely."
ssh @sshOptions -i $SshKeyPath "$SshUser@$MasterIp" "kubectl --request-timeout=20s -n smart-interviewer get pods,svc,pvc"
if ($LASTEXITCODE -ne 0) {
    throw "Remote verification failed"
}
