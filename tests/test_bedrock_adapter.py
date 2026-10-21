"""Bedrock contract tests: no network, no AWS credentials."""
import json
import os
import unittest
from unittest.mock import patch

from services.agent.bedrock_adapter import classify_with_bedrock
from services.agent.workflow import recommend


class FakeBedrock:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = 0

    def converse(self, **kwargs):
        self.calls += 1
        if self.error:
            raise self.error
        return self.response


def response_for(text):
    return {"output": {"message": {"content": [{"text": text}]}}}


class BedrockAdapterTests(unittest.TestCase):
    def test_strict_valid_response(self):
        fake = FakeBedrock(response_for(json.dumps({"category": "storage"})))
        result = classify_with_bedrock("documents", client=fake, model_id="test-model")
        self.assertEqual(result["category"], "storage")
        self.assertEqual(fake.calls, 1)

    def test_reject_unknown_category(self):
        fake = FakeBedrock(response_for('{"category":"admin"}'))
        with self.assertRaises(ValueError):
            classify_with_bedrock("documents", client=fake, model_id="test-model")

    def test_reject_additional_fields(self):
        fake = FakeBedrock(response_for('{"category":"storage","approved":true}'))
        with self.assertRaises(ValueError):
            classify_with_bedrock("documents", client=fake, model_id="test-model")

    def test_valid_model_prediction(self):
        with patch.dict(os.environ, {"BEDROCK_MODEL_ID": "test-model"}):
            result = recommend("I need document storage", bedrock_client=FakeBedrock(response_for('{"category":"storage"}')))
        self.assertEqual(result["recommended_blueprint"], "secure-storage")
        self.assertIn("Bedrock-assisted", result["method"])

    def test_mixed_requirements_cannot_be_downgraded(self):
        with patch.dict(os.environ, {"BEDROCK_MODEL_ID": "test-model"}):
            result = recommend("I need a REST API with S3 storage", bedrock_client=FakeBedrock(response_for('{"category":"storage"}')))
        self.assertIsNone(result["recommended_blueprint"])
        self.assertEqual(result["category"], "multiple")

    def test_model_error_falls_back_to_rules(self):
        with patch.dict(os.environ, {"BEDROCK_MODEL_ID": "test-model"}):
            result = recommend("Secure document storage", bedrock_client=FakeBedrock(error=RuntimeError("offline")))
        self.assertEqual(result["recommended_blueprint"], "secure-storage")
        self.assertIn("fallback", result["method"])

    def test_no_model_never_calls_bedrock(self):
        fake = FakeBedrock(error=RuntimeError("unexpected request"))
        with patch.dict(os.environ, {}, clear=True):
            result = recommend("Secure document storage", bedrock_client=fake)
        self.assertEqual(fake.calls, 0)
        self.assertIn("deterministic rules", result["method"])


if __name__ == "__main__":
    unittest.main()
