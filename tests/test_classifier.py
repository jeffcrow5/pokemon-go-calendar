import unittest
from unittest.mock import Mock, patch

from classifier import classify_article


class ClassifyArticleTests(unittest.TestCase):
    @patch("classifier.requests.post")
    def test_enables_thinking_and_parses_json_content(self, post):
        result = {"event_types": []}
        response = Mock()
        response.json.return_value = {
            "message": {
                "content": '{"event_types": []}',
            },
        }
        post.return_value = response

        classification = classify_article("Article text")

        self.assertEqual(classification, result)
        payload = post.call_args.kwargs["json"]
        self.assertTrue(payload["think"])
        self.assertEqual(payload["format"], "json")

    @patch("classifier.requests.post")
    def test_empty_model_response_raises_clear_error(self, post):
        response = Mock()
        response.json.return_value = {
            "message": {
                "content": "",
            },
            "done_reason": "length",
        }
        post.return_value = response

        with self.assertRaisesRegex(
            ValueError,
            "empty classification response.*done_reason='length'",
        ):
            classify_article("Article text")

    @patch("classifier.requests.post")
    def test_invalid_json_raises_clear_error(self, post):
        response = Mock()
        response.json.return_value = {
            "message": {
                "content": "not JSON",
            },
        }
        post.return_value = response

        with self.assertRaisesRegex(
            ValueError,
            "invalid JSON",
        ):
            classify_article("Article text")


if __name__ == "__main__":
    unittest.main()
