# Initial threat model (draft)

## Key risks

- Prompt injection or compromised input persuades an agent to request unsafe infrastructure.
- Plan differs from approved blueprint, or from the artifact approved by reviewer.
- Excessive IAM privileges on provisioning workers.
- Policy evaluation outage bypasses validation.
- Exposure of sensitive Terraform state or plan content.
- Runaway deployment cost or orphaned sandbox resources.

## Planned controls

Allowlisted modules; mandatory plan-time OPA checks; deny on unavailable policy service; execution-role separation; immutable plan approval; encrypted and access-controlled artifact storage; finite sandbox quotas and teardown capability.

No threat mitigation is claimed to be implemented at Milestone 0.
