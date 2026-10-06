import unittest

from classifier_prompt import EVENT_TYPES
from rules import evaluate_event


RULES = {
    "monthly_go_pass": "ignore",
    "weekly_go_pass": "invite",
    "saturday_event": "invite",
    "settings": {
        "home_location": {
            "city": "Example City",
            "state": "Example State",
            "country": "United States",
        },
    },
}


def make_classification(event_type):
    return {
        "event_types": [event_type],
        "start": "2099-10-10T10:00:00",
        "end": "2099-10-17T10:00:00",
        "is_cancellation": False,
    }


class GoPassRuleTests(unittest.TestCase):
    def test_classifier_supports_monthly_and_weekly_pass_types(self):
        self.assertIn("monthly_go_pass", EVENT_TYPES)
        self.assertIn("weekly_go_pass", EVENT_TYPES)
        self.assertNotIn("go_pass_event", EVENT_TYPES)
        self.assertNotIn("go_pass", EVENT_TYPES)

    def test_monthly_pass_is_ignored_even_when_it_starts_on_saturday(self):
        result = evaluate_event(
            make_classification("monthly_go_pass"),
            rules=RULES,
        )

        self.assertEqual(result["action"], "ignore")

    def test_weekly_pass_is_invited(self):
        result = evaluate_event(
            make_classification("weekly_go_pass"),
            rules=RULES,
        )

        self.assertEqual(result["action"], "invite")


if __name__ == "__main__":
    unittest.main()
