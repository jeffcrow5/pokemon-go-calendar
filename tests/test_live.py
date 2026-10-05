import json

from classifier import (
    fetch_article,
    classify_article,
    validate_result,
)
from state import (
    load_state,
    get_article_id,
    get_event_id,
    is_article_known,
    get_event,
    record_article,
)


TEST_URL = "https://pokemongo.com/en/news/go-pass-october-2026"


def main():
    state = load_state()

    article = {
        "title": "GO Pass: October",
        "url": TEST_URL,
        "published_at": None,
    }

    article_id = get_article_id(article)

    print("=" * 80)
    print("LIVE ARTICLE TEST")
    print("=" * 80)
    print(f"URL:        {article['url']}")
    print(f"ARTICLE ID: {article_id}")
    print()

    if is_article_known(state, article_id):
        print("This article is already in state.json.")
        print()

        existing_article = state["articles"][article_id]
        event_id = existing_article.get("event_id")

        if event_id:
            print(f"EVENT ID: {event_id}")

        return

    print("Fetching article...")
    article_text = fetch_article(article["url"])

    print(f"Extracted {len(article_text):,} characters.")
    print()

    print("Classifying article...")
    result = classify_article(article_text)
    validate_result(result)

    print()
    print("CLASSIFICATION")
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()

    event_id = get_event_id(result)
    existing_event = get_event(state, event_id)

    print(f"ARTICLE ID: {article_id}")
    print(f"EVENT ID:   {event_id}")
    print()

    if existing_event:
        print("EVENT STATUS: EXISTING EVENT")
        print(f"Event name: {existing_event['event_name']}")
    else:
        print("EVENT STATUS: NEW EVENT")

        state["events"][event_id] = {
            "event_name": result["event_name"],
            "article_ids": [],
        }

    record_article(
        state,
        article,
        article_id,
        event_id,
    )

    from state import save_state
    save_state(state)

    print()
    print("State saved successfully.")


if __name__ == "__main__":
    main()