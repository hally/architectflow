# ArchitectFlow AWS Infrastructure — Terraform-only

This folder defines an AWS hosting **target architecture** for ArchitectFlow. It requires **no AWS account to author or format**. No resource is provisioned until someone explicitly runs `terraform apply` with AWS credentials.

## Architecture

- VPC with two public subnets in different Availability Zones, route table and internet gateway.
- Internet-facing Application Load Balancer (HTTP only for demonstration).
- ECS Fargate cluster, task definition and service for the existing Flask/LangGraph/OPA portal.
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
2. Build a container image containing Python dependencies, **gunicorn**, the OPA executable at `/usr/local/bin/opa`, and the complete ArchitectFlow source under `/app` (including `portal`, `services`, `policies`, `terraform/modules`). It must be writable to `/app/instance` via UID/GID 1000 on EFS.
3. Push that image to the ECR repository output by this root module. The service starts at `desired_count = 0` by default, allowing infrastructure creation before the image exists.
4. Create an AWS Secrets Manager secret with a strong Flask secret key and supply `flask_secret_arn`. Do not write the secret value in Terraform configuration/state.
5. Set `desired_count = 1` only after the container image and secret are ready.
6. For actual users, configure HTTPS (ACM/ALB 443), authentication, authorization, CSRF protection, secure session handling, hardened images and restricted network access. **This demo's HTTP listener must not be used with real credentials or data.**
7. Replace SQLite/EFS with an appropriate managed database for multi-task or production operation. The Flask application needs corresponding database code changes.
8. Enable a cost budget and inspect AWS pricing before deployment. Budgets do **not** cap spending. ALB, EFS, storage and other AWS resources may incur ongoing costs even with `desired_count = 0`.

## Security boundaries

- This starter intentionally avoids a NAT gateway by assigning public IPs to Fargate tasks, while security groups allow application ingress **only from the ALB**. This is a demo cost tradeoff, not a recommended production network perimeter.
- The public HTTP endpoint is not suitable for sensitive workloads. Do not deploy this as-is to serve real customers.
- Terraform source checks currently cover the secure-storage S3 module; they do **not** establish compliance of this entire hosting stack or an applied AWS environment.
- Encryption of EFS is enabled. CloudWatch logs and task IAM policies are defined but require review before production.
