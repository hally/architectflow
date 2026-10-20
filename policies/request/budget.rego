package architectflow.request

import rego.v1

# Example monthly request ceilings in USD; these are not AWS pricing estimates.
budget_limits := {"development": 200, "staging": 500, "production": 2000}

default allow := false

budget_allowed if {
    limit := budget_limits[input.environment]
    is_number(input.budget)
    input.budget > 0
    input.budget <= limit
}

allow if {
    region_allowed
    budget_allowed
}

deny contains "AWS region is not on the approved list" if {
    not region_allowed
}

deny contains "Environment is missing or not approved" if {
    not input.environment in {"development", "staging", "production"}
}

deny contains "Monthly requested budget exceeds the environment limit or is invalid" if {
    input.environment in {"development", "staging", "production"}
    not budget_allowed
}
