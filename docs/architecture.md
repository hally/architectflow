# Architecture overview

## Planned request lifecycle

1. Developer submits a request via Flask.
2. LangGraph gathers requirements and selects an approved blueprint.
3. OPA validates request constraints.
4. A separate Terraform runner creates a saved plan.
5. OPA validates the plan JSON, with deny-by-default for missing evidence.
6. The pricing service assesses costs against a budget.
7. The user reviews outcomes; an authorized approver approves a specific plan.
8. A dedicated runner applies the exact approved plan in a sandbox account.
9. The platform stores audit events and supports resource destruction.

## Trust boundaries

- AI orchestration has no privileged AWS provisioning credentials.
- The Terraform execution role is separate from the portal role.
- Only allowlisted blueprints are accepted.
- Sensitive plan artifacts and Terraform state are secured outside Git.
- Deployment is off by default until explicit approval gates exist.

This document describes the target architecture, not implemented features.
