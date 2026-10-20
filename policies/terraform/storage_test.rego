package architectflow.terraform

import rego.v1

compliant := {
    "resource_count": 5,
    "resources": {
        "aws_s3_bucket.documents": {
            "bucket": "${var.bucket_name}",
            "tags": {
                "Project": "${var.project}",
                "Environment": "${var.environment}",
                "Owner": "${var.owner}",
                "CostCenter": "${var.cost_center}"
            }
        },
        "aws_s3_bucket_public_access_block.documents": {
            "bucket": "${aws_s3_bucket.documents.id}",
            "block_public_acls": true,
            "ignore_public_acls": true,
            "block_public_policy": true,
            "restrict_public_buckets": true
        },
        "aws_s3_bucket_server_side_encryption_configuration.documents": {
            "bucket": "${aws_s3_bucket.documents.id}",
            "rule": [{"apply_server_side_encryption_by_default": [{"sse_algorithm": "AES256"}]}]
        },
        "aws_s3_bucket_ownership_controls.documents": {
            "bucket": "${aws_s3_bucket.documents.id}",
            "rule": [{"object_ownership": "BucketOwnerEnforced"}]
        }
    }
}

test_compliant_configuration_allowed if {
    allow with input as compliant
}

test_public_bucket_policy_disabled_denied if {
    not allow with input as object.union(compliant, {
        "resources": object.union(compliant.resources, {
            "aws_s3_bucket_public_access_block.documents": object.union(
                compliant.resources["aws_s3_bucket_public_access_block.documents"],
                {"block_public_policy": false}
            )
        })
    })
}

test_missing_encryption_denied if {
    # object.union recursively merges objects, which would restore the deleted key.
    # Remove "resources" from the outer object first to replace it entirely.
    base := object.remove(compliant, {"resources"})
    resources_without_encryption := object.remove(
        compliant.resources,
        {"aws_s3_bucket_server_side_encryption_configuration.documents"}
    )
    modified := object.union(base, {"resources": resources_without_encryption})
    not allow with input as modified
}

test_missing_tags_denied if {
    # Replace the bucket resource rather than recursively merging its tags.
    base := object.remove(compliant, {"resources"})
    other_resources := object.remove(compliant.resources, {"aws_s3_bucket.documents"})
    modified_resources := object.union(other_resources, {
        "aws_s3_bucket.documents": {
            "bucket": "${var.bucket_name}",
            "tags": {"Project": "${var.project}"}
        }
    })
    modified := object.union(base, {"resources": modified_resources})
    not allow with input as modified
}

test_missing_everything_denied if {
    not allow with input as {}
}
