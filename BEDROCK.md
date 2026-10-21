# Optional Bedrock-assisted architecture classification

ArchitectFlow remains fully functional without an AWS account. By default, the LangGraph planner uses its **deterministic local rules**, and OPA independently evaluates request and Terraform-source security policies.

## Optional Bedrock path (not live-tested)

- Enable only by setting `BEDROCK_MODEL_ID` to an authorized Bedrock Converse model ID or inference profile ID, and `AWS_REGION` to the target AWS region.
- The ECS Terraform module exposes `bedrock_model_id` for this purpose; model access is scoped separately using `bedrock_model_arns`. The two values must refer to a compatible permitted model or inference profile.
- The service uses the AWS SDK default credential chain (the ECS **task role** when deployed). Never place credentials in Terraform variables or the container image.
- Bedrock returns a JSON category, not executable Terraform, AWS resources, budget approvals or OPA decisions.
- Responses are strictly validated to `storage`, `api`, `multiple` or `unknown`. Extra fields and unexpected output cause deterministic fallback.
- For unambiguous local classifications, disagreement also falls back to deterministic rules. A known mixed API/storage request cannot be downgraded to a single blueprint.
- The saved request audit shows whether a recommendation used Bedrock, deterministic rules, or fallback. Policy evaluation remains separate.
- If Bedrock is unavailable, the application remains operational on rules; fallback is not represented as a successful Bedrock invocation.
- External prose is untrusted data. These controls limit the allowed outputs but are **not** a complete prompt-injection defense.

## Offline verification

The test suite uses an injected fake Bedrock client, not mock AWS services or credentials:

```sh
python -m unittest discover -s tests -v
```

The GitHub Actions pipeline also validates OPA policies, Terraform and the container build. These do not establish live Bedrock access, model quality, latency, regional availability, or runtime credentials.

## Architecture boundaries

```text
Developer requirements
        |
   LangGraph planner
        |---- deterministic classifier (always available)
        |---- optional Bedrock Converse classifier (configured only)
        v
  Allowed catalog category
        |
  Blueprint recommendation
        |
   Human request submission
        |
  OPA request evaluation + Terraform source validation
        |
  SQLite audit / provenance
```

The Serverless API catalog entry remains **not implemented** as Terraform; neither AI nor policy checks authorize its deployment.

## Future deployment checks

Before a real AWS deployment, verify Converse support for the chosen model and region, IAM permissions for the exact runtime resource, private Bedrock VPC endpoint availability and connectivity, logs/observability, invocation cost controls, and response behavior under timeout/throttling. AWS account access is required for those checks.
