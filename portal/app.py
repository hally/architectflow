"""ArchitectFlow local MVP with independent OPA request-policy evaluation.

Development-only portal. This service DOES NOT provision AWS infrastructure.
"""
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for
from infra_policy import inspect_blueprint

# Preserve Flask's existing local instance path unless an explicit container
# storage path is supplied. ECS mounts EFS at /app/portal/instance.
app = Flask(__name__, instance_path=os.environ.get("ARCHITECTFLOW_INSTANCE_PATH"))
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "local-development-only-not-for-production")
DB_PATH = Path(app.instance_path) / "architectflow.db"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Running "python portal/app.py" puts portal/ (not the repo root) on sys.path.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from services.agent.workflow import recommend
OPA_POLICY_DIR = PROJECT_ROOT / "policies" / "request"
OPA_EXECUTABLE = os.environ.get(
    "OPA_EXECUTABLE", str(Path.home() / "Tools" / "OPA" / "opa.exe")
)
BLUEPRINTS = {
    "secure-storage": "Secure document storage (S3)",
    "serverless-api": "Serverless API (API Gateway + Lambda)",
}
# Include a deliberately unapproved region so the policy rejection can be demonstrated.
REGIONS = {
    "ca-central-1": "Canada (Central)",
    "ca-west-1": "Canada (West)",
    "us-east-1": "US East (policy test: blocked)",
}
ENVIRONMENTS = {
    "development": "Development — $200 max",
    "staging": "Staging — $500 max",
    "production": "Production — $2,000 max",
}


def db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create or migrate the local schema without destroying existing requests."""
    with db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS infrastructure_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                owner TEXT NOT NULL,
                blueprint TEXT NOT NULL,
                region TEXT NOT NULL,
                budget REAL NOT NULL,
                notes TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        existing_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(infrastructure_requests)")
        }
        if "environment" not in existing_columns:
            conn.execute(
                "ALTER TABLE infrastructure_requests ADD COLUMN environment TEXT"
            )
        if "policy_reasons" not in existing_columns:
            conn.execute(
                "ALTER TABLE infrastructure_requests ADD COLUMN policy_reasons TEXT"
            )
        if "config_status" not in existing_columns:
            conn.execute(
                "ALTER TABLE infrastructure_requests ADD COLUMN config_status TEXT"
            )
        if "config_reasons" not in existing_columns:
            conn.execute(
                "ALTER TABLE infrastructure_requests ADD COLUMN config_reasons TEXT"
            )
        # Nullable fields preserve historical requests unchanged.
        for column in ("planner_requirements", "planner_category", "planner_blueprint",
                       "planner_explanation", "planner_method"):
            if column not in existing_columns:
                conn.execute(f"ALTER TABLE infrastructure_requests ADD COLUMN {column} TEXT")
        for column in ("terraform_source_sha256", "terraform_evaluated_at"):
            if column not in existing_columns:
                conn.execute(f"ALTER TABLE infrastructure_requests ADD COLUMN {column} TEXT")


def evaluate_policy(payload):
    """Evaluate actual Rego rules via OPA; unavailable/invalid results fail closed."""
    try:
        result = subprocess.run(
            [
                OPA_EXECUTABLE,
                "eval",
                "--format=json",
                "-d", str(OPA_POLICY_DIR),
                "-I",
                "data.architectflow.request",
            ],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            timeout=10,
            check=True,
        )
        output = json.loads(result.stdout)
        expressions = output.get("result", [{}])[0].get("expressions", [])
        if len(expressions) != 1:
            raise ValueError("OPA returned no single policy result")
        decision = expressions[0].get("value", {})
        if not isinstance(decision, dict) or not isinstance(decision.get("allow"), bool):
            raise ValueError("OPA decision did not contain a boolean allow")
        reasons = decision.get("deny", [])
        if not isinstance(reasons, list) or any(not isinstance(x, str) for x in reasons):
            raise ValueError("OPA decision reasons were invalid")
        if decision["allow"]:
            return "Request policy approved", []
        return "Request policy denied", sorted(reasons) or ["Request denied by policy"]
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired,
            ValueError, KeyError, IndexError, TypeError, json.JSONDecodeError):
        app.logger.exception("OPA evaluation failed; request will not be approved")
        return "Policy evaluation error", ["Policy engine unavailable or returned an invalid decision"]


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        project_name = request.form.get("project_name", "").strip()
        owner = request.form.get("owner", "").strip()
        blueprint = request.form.get("blueprint", "")
        region = request.form.get("region", "")
        environment = request.form.get("environment", "")
        notes = request.form.get("notes", "").strip()

        try:
            budget = float(request.form.get("budget", ""))
        except ValueError:
            budget = -1

        if not (1 <= len(project_name) <= 80 and 1 <= len(owner) <= 80):
            flash("Enter a project name and owner (maximum 80 characters each).", "danger")
        elif blueprint not in BLUEPRINTS or region not in REGIONS:
            flash("Select an available blueprint and region.", "danger")
        elif environment not in ENVIRONMENTS:
            flash("Select an environment.", "danger")
        elif not (0 < budget <= 1000000):
            flash("Enter a valid monthly budget above $0 and at most $1,000,000.", "danger")
        elif len(notes) > 1000:
            flash("Requirements must be 1,000 characters or fewer.", "danger")
        else:
            status, reasons = evaluate_policy({
                "project_name": project_name,
                "owner": owner,
                "blueprint": blueprint,
                "region": region,
                "environment": environment,
                "budget": budget,
            })
            # Blueprint inspection is independent from the request policy.
            # It checks the checked-in module source, not planned AWS changes.
            config_status, config_reasons, terraform_sha, terraform_checked_at = inspect_blueprint(blueprint)
            planner = session.pop("architecture_recommendation", None)
            # Attribute a recommendation only if the selected blueprint matches.
            matched = (
                isinstance(planner, dict)
                and planner.get("recommended_blueprint") == blueprint
                and blueprint in BLUEPRINTS
            )
            audit = planner if matched else {}
            with db_connection() as conn:
                conn.execute(
                    """INSERT INTO infrastructure_requests
                    (project_name, owner, blueprint, region, environment, budget,
                     notes, status, policy_reasons, config_status, config_reasons,
                     planner_requirements, planner_category, planner_blueprint,
                     planner_explanation, planner_method, terraform_source_sha256,
                     terraform_evaluated_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (project_name, owner, blueprint, region, environment, budget,
                     notes, status, json.dumps(reasons), config_status,
                     json.dumps(config_reasons),
                     audit.get("requirements"), audit.get("category"),
                     audit.get("recommended_blueprint"), audit.get("explanation"),
                     "LangGraph / deterministic rules v1" if matched else None,
                     terraform_sha, terraform_checked_at,
                     datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")),
                )
            flash(f"Request saved: {status}.", "success" if status == "Request policy approved" else "warning")
            return redirect(url_for("home"))

    planner = session.get("architecture_recommendation")
    if isinstance(planner, dict):
        return render_home(planner, planner.get("requirements", ""))
    return render_home()


def render_home(recommendation=None, requirements_text=""):
    with db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM infrastructure_requests ORDER BY id DESC"
        ).fetchall()
    requests = []
    for row in rows:
        item = dict(row)
        try:
            item["reasons"] = json.loads(item.get("policy_reasons") or "[]")
        except (ValueError, TypeError):
            item["reasons"] = []
        try:
            item["config_reasons_list"] = json.loads(item.get("config_reasons") or "[]")
        except (ValueError, TypeError):
            item["config_reasons_list"] = []
        requests.append(item)

    return render_template(
        "index.html",
        requests=requests,
        recommendation=recommendation,
        requirements_text=requirements_text,
        blueprints=BLUEPRINTS,
        regions=REGIONS,
        environments=ENVIRONMENTS,
        pending_count=sum(r["status"] == "Pending validation" for r in requests),
        approved_count=sum(r["status"] == "Request policy approved" for r in requests),
    )


@app.route("/recommend", methods=["POST"])
def recommend_blueprint():
    requirements = request.form.get("requirements", "").strip()
    if not requirements:
        flash("The Architecture Planner field is empty. Enter requirements in the box above the Recommend architecture button.", "danger")
        return redirect(url_for("home"))
    if len(requirements) > 1000:
        flash("Architecture Planner requirements must be 1,000 characters or fewer.", "danger")
        return redirect(url_for("home"))
    try:
        recommendation = recommend(requirements)
    except Exception:
        app.logger.exception("LangGraph recommendation failed")
        flash("Architecture recommendation unavailable. No blueprint was selected.", "danger")
        return redirect(url_for("home"))
    session["architecture_recommendation"] = {
        "requirements": requirements,
        "category": recommendation.get("category"),
        "recommended_blueprint": recommendation.get("recommended_blueprint"),
        "explanation": recommendation.get("explanation"),
    }
    return redirect(url_for("home"))


initialize_database()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
