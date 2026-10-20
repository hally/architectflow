"""Architecture selection graph tests. Run: python -m unittest discover -s tests -v"""
import unittest

from services.agent.workflow import recommend


class ArchitectureGraphTests(unittest.TestCase):
    def test_storage(self):
        result = recommend("Private encrypted document storage in S3")
        self.assertEqual(result["recommended_blueprint"], "secure-storage")
        self.assertEqual(result["category"], "storage")

    def test_api(self):
        result = recommend("A REST API with several endpoints")
        self.assertEqual(result["recommended_blueprint"], "serverless-api")
        self.assertIn("not implemented", result["explanation"])

    def test_ambiguous_request(self):
        result = recommend("REST API to upload documents to S3")
        self.assertIsNone(result["recommended_blueprint"])
        self.assertEqual(result["category"], "multiple")

    def test_unknown_request(self):
        result = recommend("I need something for the engineering team")
        self.assertIsNone(result["recommended_blueprint"])
        self.assertEqual(result["category"], "unknown")


if __name__ == "__main__":
    unittest.main()
