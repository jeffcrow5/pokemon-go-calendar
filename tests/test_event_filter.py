from datetime import datetime

from event_filter import (
    extract_event_end,
    event_has_ended,
)


CURRENT_DATETIME = datetime.fromisoformat(
    "2026-10-05T19:00:00"
)


def run_test(name, article_text, expected_end, expected_ended):
    event_end = extract_event_end(article_text)

    print(f"{name}:")
    print(f"  Event end: {event_end}")
    print(f"  Expected:  {expected_end}")

    if expected_end is None:
        assert event_end is None
    else:
        assert event_end == datetime.fromisoformat(
            expected_end
        )

    ended = event_has_ended(
        article_text,
        CURRENT_DATETIME,
    )

    print(f"  Ended:     {ended}")
    print(f"  Expected:  {expected_ended}")
    print()

    assert ended == expected_ended


def main():
    run_test(
        "Past event",
        """
        Pokémon GO Community Day will take place October 3-4, 2026.
        The event runs from 2:00 p.m. to 5:00 p.m. local time each day.
        """,
        "2026-10-04T17:00:00",
        True,
    )

    run_test(
        "Future event",
        """
        Pokémon GO Community Day will take place October 10-11, 2026.
        The event runs from 2:00 p.m. to 5:00 p.m. local time each day.
        """,
        "2026-10-11T17:00:00",
        False,
    )

    run_test(
        "Currently ongoing",
        """
        Pokémon GO Community Day is happening October 5, 2026,
        from 10:00 a.m. to 10:00 p.m. local time.
        """,
        "2026-10-05T22:00:00",
        False,
    )

    run_test(
        "No event date",
        """
        Pokémon GO Tour 2027 has been announced.
        More information about the event will be revealed later.
        """,
        None,
        False,
    )

    run_test(
        "Past date mentioned but future event",
        """
        Trainers can look back at last year's event on October 3.
        The 2026 event will take place October 10-11, 2026,
        from 2:00 p.m. to 5:00 p.m. local time.
        """,
        "2026-10-11T17:00:00",
        False,
    )

    run_test(
        "Rescheduled event",
        """
        The event originally scheduled for October 3 has been
        rescheduled. It will now take place October 10, 2026,
        from 10:00 a.m. to 6:00 p.m. local time.
        """,
        "2026-10-10T18:00:00",
        False,
    )

    print("All event filter tests passed.")


if __name__ == "__main__":
    main()