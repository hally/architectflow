package architectflow.request

import rego.v1

# Approved deployment boundaries for the demonstration enterprise.
approved_regions := {"ca-central-1", "ca-west-1"}

region_allowed if {
    input.region in approved_regions
}
