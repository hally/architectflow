# ArchitectFlow

**Policy-governed, AI-assisted self-service AWS infrastructure provisioning.**

ArchitectFlow will allow engineering teams to request approved AWS infrastructure through a Python/Flask portal. LangGraph will guide requirements collection and architecture selection; Open Policy Agent (OPA) will independently enforce policy; Terraform will produce reviewable plans and provision infrastructure only after authorization.

> **Status:** Milestone 0 — repository scaffold. No operational provisioning code is included yet. Terraform apply is not enabled.

## Technology stack

- Portal and API: Python, Flask, Jinja2, Bootstrap
- Workflow orchestration: LangGraph; Amazon Bedrock planned for model inference
- Governance: OPA/Rego policy-as-code
- Infrastructure: AWS and Terraform
- CI: GitHub Actions (checks to be added after implementation)

## Initial architecture blueprints

1. **Secure document storage:** S3, KMS, IAM; optional authenticated CloudFront delivery.
2. **Serverless REST API:** API Gateway, Lambda, DynamoDB, CloudWatch, IAM.

## Operating principles

1. AI may recommend designs; it never grants deployment authorization.
2. Only reviewed Terraform modules are eligible for provisioning.
3. OPA must evaluate the actual Terraform plan, not only the initial request.
4. Policy errors and missing mandatory evidence block deployment.
5. Approval must bind to an immutable saved plan, policy version, cost estimate and requester.
6. No production accounts or paid AWS infrastructure without explicit approval.

## Roadmap

- **M0 — Repository foundation:** layout, README, baseline configuration.
- **M1 — OPA security validation:** generate a real S3 Terraform plan; reject public storage; pass corrected plan.
- **M2 — LangGraph:** interpret requests and select approved modules.
- **M3 — Flask portal:** create and inspect requests, policy outcomes, and approvals.
- **M4 — Cost governance:** itemized estimates and budget checks.
- **M5 — Sandbox deployment:** approved plan application, audit logging and cleanup.
- **M6 — Enterprise demonstration:** tests, documentation and measured outcomes.

## Folder map

- `portal/` — Flask application and HTML templates
- `services/agent/` — LangGraph workflow
- `services/policy/` — OPA integration
- `services/pricing/` — cost estimation
- `services/provisioning/` — controlled Terraform orchestration
- `policies/` — Rego source and policy tests
- `terraform/modules/` — approved AWS blueprints
- `docs/` — decisions, threat model, architecture
- `tests/` — Python integration/unit tests

## Getting started

This commit is a **scaffold**, not a running application. Next, implement the secure storage Terraform module and its OPA policy tests. Do not commit credentials, Terraform state files, plan files, or real enterprise data.

## License

No license selected. All rights reserved until one is explicitly chosen.
