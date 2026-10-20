"""Export a narrow, reviewable HCL configuration snapshot for OPA.

Only inspects locally authored Terraform source. No AWS credentials or plan needed.
This is a configuration precheck, not a replacement for plan-time checks.
"""
import argparse
import json
from pathlib import Path

import hcl2


def load_resources(module_dir: Path):
    resources = {}
    for path in sorted(module_dir.glob("*.tf")):
        with path.open("r", encoding="utf-8") as file:
            document = hcl2.load(file)
        for group in document.get("resource", []):
            for resource_type, instances in group.items():
                for name, attributes in instances.items():
                    key = f"{resource_type}.{name}"
                    if key in resources:
                        raise ValueError(f"Duplicate resource: {key}")
                    resources[key] = attributes
    return resources


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", default="terraform/modules/secure-storage")
    parser.add_argument("--out", default="build/secure-storage-policy-input.json")
    args = parser.parse_args()

    module_dir = Path(args.module)
    if not module_dir.is_dir():
        parser.error(f"Module directory does not exist: {module_dir}")
    resources = load_resources(module_dir)
    output = {
        "resource_count": len(resources),
        "resources": resources,
    }
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Exported {len(resources)} Terraform resources to {destination}")


if __name__ == "__main__":
    main()
