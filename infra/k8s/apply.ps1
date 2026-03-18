$ErrorActionPreference = 'Stop'

function Apply-Manifest {
	param(
		[Parameter(Mandatory = $true)]
		[string]$Path
	)

	Write-Host "Applying $Path ..."
	kubectl apply -f $Path
	if ($LASTEXITCODE -ne 0) {
		throw "kubectl apply failed for $Path"
	}
}

Apply-Manifest "00-namespace.yaml"
Apply-Manifest "01-db-secret.yaml"
Apply-Manifest "02-db-pvc.yaml"
Apply-Manifest "03-db-service.yaml"
Apply-Manifest "04-db-statefulset.yaml"
Apply-Manifest "06-backend-service.yaml"
Apply-Manifest "05-backend-deployment.yaml"
Apply-Manifest "07-frontend-deployment.yaml"
Apply-Manifest "08-frontend-service.yaml"

Write-Host "All manifests applied."
kubectl -n smart-interviewer get pods,svc,pvc
if ($LASTEXITCODE -ne 0) {
	throw "kubectl get verification failed"
}
