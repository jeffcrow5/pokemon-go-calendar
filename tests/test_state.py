from state import (
    get_article_id,
    get_event_id,
    is_article_known,
    get_event,
    record_article,
)


def make_article(url, title):
    return {
        "url": url,
        "title": title,
        "published_at": None,
    }


def make_classification(event_name):
    return {
        "event_name": event_name,
    }


def main():
    state = {
        "articles": {},
        "events": {},
    }

    print("=" * 80)
    print("TEST 1: New article creates a new event")
    print("=" * 80)

    article_1 = make_article(
        "https://example.com/news/community-day-zorua",
        "October 2026 Community Day: Zorua",
    )

    classification_1 = make_classification(
        "October 2026 Community Day: Zorua"
    )

    article_id_1 = get_article_id(article_1)
    event_id_1 = get_event_id(classification_1)

    print(f"Article ID: {article_id_1}")
    print(f"Event ID:   {event_id_1}")

    assert not is_article_known(state, article_id_1)

    state["events"][event_id_1] = {
        "event_name": classification_1["event_name"],
        "article_ids": [],
    }

    record_article(
        state,
        article_1,
        article_id_1,
        event_id_1,
    )

    assert is_article_known(state, article_id_1)
    assert get_event(state, event_id_1) is not None

    print("PASS")
    print()


    print("=" * 80)
    print("TEST 2: Same article is recognized as already processed")
    print("=" * 80)

    assert is_article_known(state, article_id_1)

    print("PASS")
    print()


    print("=" * 80)
    print("TEST 3: Different article for same event uses same event ID")
    print("=" * 80)

    article_2 = make_article(
        "https://example.com/news/community-day-zorua-update",
        "October 2026 Community Day: Zorua — Update",
    )

    classification_2 = make_classification(
        "October 2026 Community Day: Zorua"
    )

    article_id_2 = get_article_id(article_2)
    event_id_2 = get_event_id(classification_2)

    print(f"Article 1 ID: {article_id_1}")
    print(f"Article 2 ID: {article_id_2}")
    print(f"Event 1 ID:   {event_id_1}")
    print(f"Event 2 ID:   {event_id_2}")

    assert article_id_1 != article_id_2
    assert event_id_1 == event_id_2
    assert get_event(state, event_id_2) is not None

    record_article(
        state,
        article_2,
        article_id_2,
        event_id_2,
    )

    assert len(state["events"][event_id_1]["article_ids"]) == 2

    print("PASS")
    print()


    print("=" * 80)
    print("TEST 4: Different event gets a different event ID")
    print("=" * 80)

    article_3 = make_article(
        "https://example.com/news/go-pass-october",
        "GO Pass: October",
    )

    classification_3 = make_classification(
        "GO Pass: October"
    )

    article_id_3 = get_article_id(article_3)
    event_id_3 = get_event_id(classification_3)

    print(f"Zorua event ID:    {event_id_1}")
    print(f"GO Pass event ID:  {event_id_3}")

    assert event_id_1 != event_id_3

    state["events"][event_id_3] = {
        "event_name": classification_3["event_name"],
        "article_ids": [],
    }

    record_article(
        state,
        article_3,
        article_id_3,
        event_id_3,
    )

    assert get_event(state, event_id_3) is not None

    print("PASS")
    print()


    print("=" * 80)
    print("TEST 5: Event ID is stable across repeated calculations")
    print("=" * 80)

    event_id_again = get_event_id(
        make_classification("October 2026 Community Day: Zorua")
    )

    assert event_id_again == event_id_1

    print("PASS")
    print()


    print("=" * 80)
    print("ALL TESTS PASSED")
    print("=" * 80)

    print()
    print("Final state:")
    import json
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()