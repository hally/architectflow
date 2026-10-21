# ECS-compatible application image. No AWS credentials needed to build.
FROM python:3.13-slim

ARG OPA_VERSION=v1.21.3

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl --fail --location --retry 3 \
       "https://github.com/open-policy-agent/opa/releases/download/${OPA_VERSION}/opa_linux_amd64_static" \
       --output /usr/local/bin/opa \
    && chmod 0755 /usr/local/bin/opa \
    && /usr/local/bin/opa version

WORKDIR /app
COPY requirements-app.txt /app/requirements-app.txt
RUN pip install --no-cache-dir -r /app/requirements-app.txt

# Include policy bundles and Terraform module source inspected by the app.
COPY portal/ /app/portal/
COPY policies/ /app/policies/
COPY services/ /app/services/
COPY terraform/modules/ /app/terraform/modules/

# Matches the ECS/EFS mount and POSIX UID/GID configured by Terraform.
RUN groupadd --gid 1000 architectflow \
    && useradd --uid 1000 --gid 1000 --home-dir /app --shell /usr/sbin/nologin architectflow \
    && mkdir -p /app/portal/instance \
    && chown -R architectflow:architectflow /app/portal/instance

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/portal \
    OPA_EXECUTABLE=/usr/local/bin/opa \
    ARCHITECTFLOW_INSTANCE_PATH=/app/portal/instance

USER architectflow
EXPOSE 8000

# Single worker while using SQLite; production requires a managed database.
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:8000", "portal.app:app"]
