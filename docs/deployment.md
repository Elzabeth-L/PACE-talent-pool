# Deployment runbook

## Provision

```bash
cd infrastructure/terraform
terraform init
terraform apply -var="allowed_http_cidr=0.0.0.0/0"
```

Terraform outputs the instance public IP and application URL. Opening HTTP to the world is acceptable only for synthetic prototype data.

## Deploy

The EC2 bootstrap installs Docker and creates a generated `.env`. From the repository root, upload and activate the source through the private artifact bucket and Systems Manager:

```powershell
./deployment/deploy.ps1
```

No inbound SSH rule is created. Use AWS Systems Manager Session Manager if host access is required.

## Verify

```bash
curl http://PUBLIC_IP/api/v1/health
curl http://PUBLIC_IP/api/v1/candidates
```

## Destroy

```bash
terraform destroy
```

Destroying the instance removes its local PostgreSQL data. Only fictional demonstration data belongs in this deployment.
