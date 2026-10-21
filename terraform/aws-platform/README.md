# ArchitectFlow AWS Infrastructure — Terraform-only

This folder defines an AWS hosting **target architecture** for ArchitectFlow. It requires **no AWS account to author or format**. No resource is provisioned until someone explicitly runs `terraform apply` with AWS credentials.

## Architecture

- VPC with public ALB subnets and isolated private ECS subnets across two Availability Zones, without an internet route from private subnets.
- Internet-facing ALB with conditional HTTPS/ACM and port 80 returning HTTP 403.
- ECS Fargate tasks in private subnets without public IP addresses; optional VPC endpoints for ECR API, ECR DKR, CloudWatch Logs, Secrets Manager, S3 and optionally Bedrock Runtime.
- ECR image repository with immutable tags and image scanning.
- CloudWatch Logs for application logs.
- Encrypted EFS access point to retain the **single-task MVP** SQLite database.
- Task execution IAM permissions; optional tightly scoped Bedrock model invocation permissions.
- Optional AWS Budgets email alert.

**No Bedrock model is deployed or invoked by this Terraform.** Existing LangGraph code remains deterministic until an explicit Bedrock adapter is developed. `bedrock_model_arns` only grants permissions to named resources.

## Offline checks

From `terraform/aws-platform`:

```powershell
terraform fmt -recursive
terraform fmt -check -recursive
```

`terraform validate` normally requires `terraform init`, which downloads the provider and may work without AWS credentials; it is not an AWS deployment. Avoid `terraform plan` / `apply` until an account is ready.

## Deployment prerequisites (future)

1. Have an AWS account, credentials and a Terraform state backend designed for access control, encryption and locking.
2. Build a container image containing Python dependencies, **gunicorn**, the OPA executable at `/usr/local/bin/opa`, and the complete ArchitectFlow source under `/app` (including `portal`, `services`, `policies`, `terraform/modules`). It must be writable to `/app/portal/instance` via UID/GID 1000 on EFS.
3. Push that image to the ECR repository output by this root module. The service starts at `desired_count = 0` by default, allowing infrastructure creation before the image exists.
4. Create an AWS Secrets Manager secret with a strong Flask secret key and supply `flask_secret_arn`. Do not write the secret value in Terraform configuration/state.
5. Set `enable_private_endpoints = true` and `desired_count = 1` only after the image, ACM certificate and secret are ready. VPC endpoints are required for private ECR image pulls, CloudWatch Logs and Secrets Manager; ECR image layers use the S3 gateway endpoint.
6. For actual users, provide a same-region ACM certificate and DNS name, plus authentication, authorization, CSRF protection, hardened images and restricted access. Without a certificate no HTTPS listener is created; port 80 responds with 403.
7. Replace SQLite/EFS with an appropriate managed database for multi-task or production operation. The Flask application needs corresponding database code changes.
8. Enable a cost budget and inspect AWS pricing before deployment. Budgets do **not** cap spending. ALB, EFS, storage and (when enabled) endpoints can incur ongoing charges even with `desired_count = 0`.

## Security boundaries

- Fargate runs in private subnets with no public IP or default internet route. An explicit `enable_private_endpoints` toggle creates the needed private endpoints; these endpoints incur hourly/data-processing charges. Bedrock Runtime endpoint is included if model ARNs are configured. Outbound calls to ordinary internet services will not work without additional egress.
- The HTTP listener rejects traffic. HTTPS and certificate configuration is only part of production security; do not serve real customer data without authentication and additional hardening.
- Terraform source checks currently cover the secure-storage S3 module; they do **not** establish compliance of this entire hosting stack or an applied AWS environment.
- Encryption of EFS is enabled. CloudWatch logs and task IAM policies are defined but require review before production.

## Networking validation limitations

Offline `terraform validate` checks Terraform structure, not regional endpoint availability, runtime image pulls or AWS reachability. Before a real deployment, validate endpoint support and costs in the selected region, container image access, security controls and TLS/DNS. The example remains untested in AWS.
