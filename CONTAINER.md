# ArchitectFlow container packaging

This container packages the working Flask application, LangGraph rules workflow, OPA binary, OPA policies and secure-storage Terraform **source**. It does not provision AWS infrastructure.

## Build and check (requires Docker, no AWS account)

```sh
docker build -t architectflow:dev .
docker run --rm --entrypoint opa architectflow:dev version
docker run --rm -e FLASK_SECRET_KEY=local-ci-only --entrypoint python architectflow:dev -c "from portal.app import app; r=app.test_client().get('/'); assert r.status_code == 200, r.status_code; print('Flask/EFS persistence path smoke test passed')"
```

Optional local HTTP run (development **only**, do not expose publicly):

```sh
docker run --rm -p 127.0.0.1:8000:8000 -e FLASK_SECRET_KEY=local-ci-only architectflow:dev
```

Visit http://127.0.0.1:8000. The development database is in the container and will be lost when it is removed unless a volume is mounted.

## AWS compatibility

- Terraform expects an image pushed to ECR with the configured `image_tag`.
- Terraform's ECS task mounts encrypted EFS at `/app/portal/instance`, the Flask database directory.
- Container runs as UID/GID 1000 for access-point ownership.
- The ECS execution role retrieves the real `FLASK_SECRET_KEY` from AWS Secrets Manager.
- OPA is installed at `/usr/local/bin/opa`.
- Terraform's ECS command overrides the image's default Gunicorn command with an equivalent invocation.

## Known limitations before production

This is an **offline-tested prototype image**. No AWS deployment has been validated. The current application lacks authentication, authorization, CSRF defenses, secure session-cookie configuration, and a production database. The selected OPA binary targets Linux amd64; the image is intended for x86_64 Fargate tasks. An optional Bedrock Converse adapter is implemented but **not live-tested**; with no model configured, LangGraph uses deterministic rules.
