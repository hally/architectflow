"""ArchitectFlow local MVP: submit and view infrastructure requests.

No AWS provisioning, AI recommendations, or policy enforcement occurs here.
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "local-development-only-not-for-production"
DB_PATH = Path(app.instance_path) / "architectflow.db"
BLUEPRINTS = {
    "secure-storage": "Secure document storage (S3)",
    "serverless-api": "Serverless API (API Gateway + Lambda)",
}
REGIONS = {"ca-central-1": "Canada (Central)", "ca-west-1": "Canada (West)"}


def db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
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


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        project_name = request.form.get("project_name", "").strip()
        owner = request.form.get("owner", "").strip()
        blueprint = request.form.get("blueprint", "")
        region = request.form.get("region", "")
        notes = request.form.get("notes", "").strip()

        try:
            budget = float(request.form.get("budget", ""))
        except ValueError:
            budget = -1

        if not (1 <= len(project_name) <= 80 and 1 <= len(owner) <= 80):
            flash("Enter a project name and owner (maximum 80 characters each).", "danger")
        elif blueprint not in BLUEPRINTS or region not in REGIONS:
            flash("Select one of the available infrastructure blueprints and regions.", "danger")
        elif not (0 < budget <= 1000000):
            flash("Enter a valid monthly budget above $0 and at most $1,000,000.", "danger")
        elif len(notes) > 1000:
            flash("Requirements must be 1,000 characters or fewer.", "danger")
        else:
            with db_connection() as conn:
                conn.execute(
                    """INSERT INTO infrastructure_requests
                    (project_name, owner, blueprint, region, budget, notes, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (project_name, owner, blueprint, region, budget, notes,
                     "Pending validation", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")),
                )
            flash("Infrastructure request saved. Policy and cost checks are not connected yet.", "success")
            return redirect(url_for("home"))

    with db_connection() as conn:
        requests = conn.execute(
            "SELECT * FROM infrastructure_requests ORDER BY id DESC"
        ).fetchall()
    return render_template(
        "index.html",
        requests=requests,
        blueprints=BLUEPRINTS,
        regions=REGIONS,
    )


initialize_database()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
