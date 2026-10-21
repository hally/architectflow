# ArchitectFlow v1.0 — Portfolio demonstration guide

**Purpose:** Demonstrate an explainable, policy-governed infrastructure self-service workflow. This is an **offline-tested prototype**. AWS Terraform is defined and validated but not deployed. The default LangGraph workflow is deterministic; the optional Bedrock adapter is tested through contract tests, not live model inference.

## Suggested 5–7 minute walkthrough

### 1. Business problem (45 sec)

Application teams need infrastructure quickly, while platform teams must enforce budget, region, and security standards. Architecture assistance should not become deployment authority.

### 2. Explain the trust boundary (45 sec)

Show the root [README architecture](../README.md#architecture). LangGraph recommends approved catalog items. OPA evaluates request constraints and real Terraform **source declarations** independently. Terraform is not applied.

### 3. Allowed storage request (60 sec)

Run the Flask portal locally. In Architecture Planner enter:

> I need secure document storage for an internal application.

Confirm **Secure document storage (S3)** and that the planner reports a rules-based method. Submit with Development, Canada Central, and $150/month. Confirm request-level **approved** and Terraform-source **validated**.

### 4. Show why AI/recommendations cannot approve infrastructure (60 sec)

Request $350/month in Development (where the current limit is $200). Confirm OPA denies the **request**, independently of the Terraform-source result. Or in a disposable local working tree set `block_public_policy = false` in the secure-storage module, submit a test request, and observe `SEC-001` infrastructure denial. Restore the file with Git and verify tests afterward.

### 5. Clarification and provenance (60 sec)

Ask:

> I need a REST API for uploading documents into secure S3 storage.

The deterministic planner identifies multiple components and asks which to select first. Expand a linked architecture decision to show original request, rationale, planning method, OPA decision and Terraform SHA-256 provenance.

### 6. CI evidence and AWS target (60 sec)

Open GitHub Actions: Terraform format/validate, OPA tests, Python/LangGraph tests, Docker build and smoke tests. Explain that these are **offline code quality controls**. Show `terraform/aws-platform`: ECS in private subnets, ALB TLS design, ECR, EFS, IAM, endpoints and optional Bedrock authorization. Explain that AWS runtime integration remains untested.

## Screenshots useful for a portfolio

- LangGraph planner with storage recommendation and method
- Combined API + storage clarification
- Request policy denial for Development over-budget
- Infrastructure source-policy denial `SEC-001`
- Expanded decision provenance showing request rationale and source SHA-256
- Four passing CI jobs

Use representative sample data only. Avoid internal corporate details, personal information or real customer records.

## Accuracy boundaries

**Demonstrated:** Local Flask UX, SQLite request history, OPA rule execution against request and parsed HCL, deterministic LangGraph classification, container smoke tests, Terraform static validation, source fingerprints and GitHub CI.

**Implemented but not exercised live:** Bedrock Converse classification with strict response contract, deterministic fallback and IAM/Terraform wiring.

**Not implemented or proved:** Terraform plan evaluation, AWS resource provisioning, AWS runtime networking, live Bedrock inference, real-world availability and throughput, financial cost estimates, production authentication or deployment authorization.

## LinkedIn series outline (five posts)

1. **Self-service shouldn't mean bypassing architecture governance.** Why request intake, recommendations and enforcement should be separate.
2. **A secure S3 design can still fail policy.** Demonstrate independent request and Terraform HCL controls, including a deliberate `SEC-001` failure.
3. **AI recommendations are advisory—not approvals.** Explain LangGraph selection, Bedrock contract and deterministic OPA enforcement.
4. **What exactly did your policy engine approve?** Explain SHA-256 source fingerprints, preserved rationale and the limits of source checks.
5. **Designing AWS infrastructure without deploying it.** ECS private subnets, TLS, endpoints, EFS trade-offs, Terraform validation, container CI, and what still requires cloud testing.

The series should clearly identify this as a **validated prototype** with an AWS infrastructure target—not a production service or a live Bedrock deployment.
