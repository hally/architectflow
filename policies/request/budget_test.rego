package architectflow.request

import rego.v1

test_compliant_development_request if {
    allow with input as {"region": "ca-central-1", "environment": "development", "budget": 150}
}

test_unapproved_region_denied if {
    not allow with input as {"region": "us-east-1", "environment": "development", "budget": 150}
}

test_development_over_budget_denied if {
    not allow with input as {"region": "ca-central-1", "environment": "development", "budget": 350}
}

test_production_approved_within_limit if {
    allow with input as {"region": "ca-west-1", "environment": "production", "budget": 1900}
}

test_missing_environment_denied if {
    not allow with input as {"region": "ca-central-1", "budget": 150}
}

test_non_numeric_budget_denied if {
    not allow with input as {"region": "ca-central-1", "environment": "development", "budget": "150"}
}

test_denial_explains_budget_violation if {
    "Monthly requested budget exceeds the environment limit or is invalid" in deny
        with input as {"region": "ca-central-1", "environment": "development", "budget": 350}
}
