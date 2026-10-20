"""Read approved Terraform module source and evaluate OPA configuration rules.

This validates the checked-in blueprint, NOT a per-request Terraform plan.
No AWS credentials, provider mocking, or provisioning are involved.
"""
import json
import os
import subprocess
from pathlib import Path

import hcl2

ROOT = Path(__file__).resolve().parents[1]
OPA_EXECUTABLE = os.environ.get("OPA_EXECUTABLE", str(Path.home() / "Tools" / "OPA" / "opa.exe"))
POLICY_DIR = ROOT / "policies" / "terraform"
MODULES = {"secure-storage": ROOT / "terraform" / "modules" / "secure-storage"}


def inspect_blueprint(blueprint):
    """Return (status, list_of_reasons); never approve on an error."""
    if blueprint not in MODULES:
        return "Not implemented", ["No Terraform configuration check exists for this blueprint yet."]

    try:
        resources = {}
        for path in sorted(MODULES[blueprint].glob("*.tf")):
            with path.open(encoding="utf-8") as stream:
                parsed = hcl2.load(stream)
            for group in parsed.get("resource", []):
                for resource_type, instances in group.items():
                    for name, attributes in instances.items():
                        key = f"{resource_type}.{name}"
                        if key in resources:
                            raise ValueError(f"Duplicate Terraform resource {key}")
                        resources[key] = attributes

        if not resources:
            raise ValueError("No Terraform resources found")

        result = subprocess.run(
            [OPA_EXECUTABLE, "eval", "-d", str(POLICY_DIR / "storage.rego"),
             "-I", "--format=json", "data.architectflow.terraform"],
            input=json.dumps({"resource_count": len(resources), "resources": resources}),
            capture_output=True, text=True, check=True, timeout=10,
        )
        expressions = json.loads(result.stdout).get("result", [{}])[0].get("expressions", [])
        if len(expressions) != 1:
            raise ValueError("OPA returned no single result")
        decision = expressions[0].get("value", {})
        if not isinstance(decision, dict) or type(decision.get("allow")) is not bool:
            raise ValueError("OPA did not return a boolean decision")
        reasons = decision.get("deny", [])
        if not isinstance(reasons, list) or not all(isinstance(x, str) for x in reasons):
            raise ValueError("OPA returned malformed denial reasons")
        if decision["allow"]:
            if reasons:
                raise ValueError("Contradictory OPA decision")
            return "Configuration validated", []
        return "Configuration denied", sorted(reasons) or ["Blueprint denied by policy"]
    except (OSError, ValueError, IndexError, KeyError, TypeError,
            subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return "Configuration check error", [f"Unable to validate blueprint locally ({type(exc).__name__})."]
