# Public release review — ArchitectFlow v1.0

## Intended public statement

**ArchitectFlow is a policy-governed AWS infrastructure design prototype, developed and tested offline.** It provides a Flask portal, deterministic LangGraph blueprint selection, optional Bedrock adapter contract, OPA governance and Terraform-source checks, SQLite audit records, an ECS-ready container and Terraform hosting definitions. The project has **not** been deployed to AWS; no real Bedrock model has been invoked; no automatic provisioning exists.

## Review completed from available repository sources

- Checked repository metadata: visibility was private at review time.
- Reviewed README, Dockerfile, application entry point, Terraform storage resources and hosting variables, sample request, GitHub Actions, ignore rules, and container/Bedrock documentation.
- No actual credential or real customer record was apparent in the examined current files. Sample values are fictional. The Flask secret shown in development examples is explicitly for local testing and **must not** be used for public deployment.
- Git ignored patterns cover `.env`, private key extensions, local instance database, virtual environments, Terraform state/variable files and downloaded providers.
- The CI pipeline now includes a full-Git-history Gitleaks scan. **Check its result before changing repository visibility.** Static scans cannot guarantee absence of secrets or sensitive details.
- Documentation distinguishes implemented offline checks from untested live AWS deployment/Bedrock integration.

## Actions before switching visibility

1. Confirm the newest GitHub Actions run has **five passing jobs**, including the Git history secret scan. Investigate and resolve findings; if a real credential was ever committed, revoke/rotate it before publishing and remove sensitive history where appropriate.
2. Perform a final human review of files and Git history for personal details, proprietary work, customer data, access keys, passwords, internal URLs, confidential screenshots, and anything not detected by automated scans. GitHub code-search results on this private repository were not exhaustive.
3. Verify that the repository has no unreviewed commits/branches/tags or GitHub Issues/Discussions containing sensitive material.
4. Decide on a software license. Currently **no license** is selected: public visibility does not grant reuse rights automatically.
5. Confirm you are comfortable publishing the code and architecture. This is an **offline-tested portfolio prototype**, not a production-ready service.
6. Only then use GitHub **Settings → General → Danger Zone → Change repository visibility → Make public**, and follow the GitHub confirmation screens. GitHub may show additional confirmation prompts.

**Publishing source is different from deploying an application.** Do not expose the Flask development server to the internet or enter real customer data in public demonstrations.

## After publishing

- Verify the repository and README display without signing in.
- Confirm GitHub Actions status and documentation links are public.
- Capture sanitized demonstration screenshots and remove any local usernames, email addresses, account identifiers or customer data.
- Publish LinkedIn Part 1 with a repository link only after the visibility change is complete.

## Features intentionally outside v1.0

Live Bedrock inference, ECR push and ECS runtime verification, AWS connectivity, Terraform plan-level policy enforcement, provisioning authorization, pricing estimates, authentication/authorization, CSRF defense, production database and multi-task availability.

These are explicitly not claimed as delivered features.
