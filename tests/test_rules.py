import json

from rules import evaluate_event, load_rules


def make_classification(
    event_name,
    event_types,
    start=None,
    end=None,
    locations=None,
    details=None,
):
    return {
        "announcement_type": "new_event",
        "primary_subject": event_name,
        "event_types": event_types,
        "event_name": event_name,
        "start": start,
        "end": end,
        "timezone": "local",
        "locations": locations or [],
        "is_update": False,
        "is_cancellation": False,
        "details": details or {},
    }


def run_test(name, classification, expected_action):
    result = evaluate_event(classification)

    actual_action = result["action"]

    print("=" * 80)
    print(name)
    print("=" * 80)
    print(f"Expected: {expected_action}")
    print(f"Actual:   {actual_action}")
    print(f"Reason:   {result['reason']}")

    if actual_action != expected_action:
        print()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise AssertionError(
            f"{name}: expected {expected_action}, got {actual_action}"
        )

    print("PASS")
    print()


def main():
    load_rules()

    run_test(
        "World Space Week",
        make_classification(
            "World Space Week 2026",
            [],
            start="2026-10-04T00:00:00",
            end="2026-10-10T23:59:00",
        ),
        "ignore",
    )

    run_test(
        "Zorua Community Day",
        make_classification(
            "October 2026 Community Day: Zorua",
            ["community_day"],
            start="2026-10-10T14:00:00",
            end="2026-10-10T17:00:00",
        ),
        "invite",
    )

    run_test(
        "Monthly GO Pass",
        make_classification(
            "GO Pass: October",
            ["monthly_go_pass"],
            start="2026-10-06T10:00:00",
            end="2026-11-03T10:00:00",
        ),
        "ignore",
    )

    run_test(
        "Weekly themed GO Pass",
        make_classification(
            "Harvest Festival GO Pass",
            ["weekly_go_pass"],
            start="2026-10-10T10:00:00",
            end="2026-10-17T10:00:00",
        ),
        "invite",
    )

    run_test(
        "Dynamax Max Battle Day",
        make_classification(
            "Dynamax Uxie, Mesprit, and Azelf Max Battle Day",
            ["dynamax_max_battle_day"],
            start="2026-10-11T14:00:00",
            end="2026-10-11T17:00:00",
        ),
        "invite",
    )

    run_test(
        "Twitch Drops",
        make_classification(
            "Pokémon Night Out",
            ["twitch_drops"],
            start="2026-10-24T19:30:00",
            end=None,
            details={
                "watch_requirements_minutes": [30, 60, 90],
                "is_online": True,
            },
        ),
        "invite",
    )

    twitch_result = evaluate_event(
        make_classification(
            "Pokémon Night Out",
            ["twitch_drops"],
            start="2026-10-24T19:30:00",
            end=None,
            details={
                "watch_requirements_minutes": [30, 60, 90],
                "is_online": True,
            },
        )
    )

    assert twitch_result["classification"]["end"] == (
        "2026-10-24T21:00:00"
    )

    run_test(
        "Nearby City Safari",
        make_classification(
            "City Safari: Salt Lake City",
            ["city_safari"],
            start="2026-10-24T10:00:00",
            end="2026-10-25T18:00:00",
            locations=["Salt Lake City, Utah, United States"],
        ),
        "invite",
    )

    run_test(
        "Distant City Safari",
        make_classification(
            "City Safari: Boston",
            ["city_safari"],
            start="2026-10-24T10:00:00",
            end="2026-10-25T18:00:00",
            locations=["Boston, Massachusetts, United States"],
        ),
        "ignore",
    )

    run_test(
        "Ignored Web Store Article",
        make_classification(
            "Pokémon GO Web Store Update",
            ["avatar_items"],
        ),
        "ignore",
    )

    print("=" * 80)
    print("ALL RULE TESTS PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()