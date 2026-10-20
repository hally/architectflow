package architectflow.terraform

import rego.v1

# Configuration-only precheck for the secure-storage Terraform blueprint.
# Fail closed: missing resources/settings, indirect or unknown expressions
# cannot satisfy the explicit checks below.
resources := object.get(input, "resources", {})

bucket := object.get(resources, "aws_s3_bucket.documents", {})
public_block := object.get(resources, "aws_s3_bucket_public_access_block.documents", {})
encryption := object.get(resources, "aws_s3_bucket_server_side_encryption_configuration.documents", {})
ownership := object.get(resources, "aws_s3_bucket_ownership_controls.documents", {})

expected_bucket_ref := "${aws_s3_bucket.documents.id}"

bucket_present if {
    object.get(input, "resource_count", 0) >= 5
    object.get(bucket, "bucket", null) != null
}

public_access_secure if {
    object.get(public_block, "bucket", "") == expected_bucket_ref
    object.get(public_block, "block_public_acls", false) == true
    object.get(public_block, "ignore_public_acls", false) == true
    object.get(public_block, "block_public_policy", false) == true
    object.get(public_block, "restrict_public_buckets", false) == true
}

encryption_secure if {
    object.get(encryption, "bucket", "") == expected_bucket_ref
    rules := object.get(encryption, "rule", [])
    count(rules) == 1
    encryption_settings := object.get(rules[0], "apply_server_side_encryption_by_default", [])
    count(encryption_settings) == 1
    object.get(encryption_settings[0], "sse_algorithm", "") == "AES256"
}

ownership_secure if {
    object.get(ownership, "bucket", "") == expected_bucket_ref
    rules := object.get(ownership, "rule", [])
    count(rules) == 1
    object.get(rules[0], "object_ownership", "") == "BucketOwnerEnforced"
}

required_tags := {"Project", "Environment", "Owner", "CostCenter"}

tags_present if {
    tags := object.get(bucket, "tags", {})
    every name in required_tags {
        object.get(tags, name, null) != null
    }
}

deny contains "SEC-001: S3 public access blocking must explicitly enable all four settings" if {
    not public_access_secure
}

deny contains "SEC-002: S3 must explicitly use AES256 server-side encryption" if {
    not encryption_secure
}

deny contains "GOV-001: S3 must declare all four ownership and cost allocation tags" if {
    not tags_present
}

deny contains "SEC-003: S3 must explicitly enforce bucket-owner object ownership" if {
    not ownership_secure
}

deny contains "ARC-001: Expected secure-storage bucket resource is missing or incomplete" if {
    not bucket_present
}

default allow := false

allow if {
    count(deny) == 0
}
