package architectflow.request

import rego.v1

# Default-deny: only explicitly approved regions are allowed.
default allow := false

approved_regions := {"ca-central-1", "ca-west-1"}

allow if {
    input.region in approved_regions
}
