import hashlib
import json
import re
from pathlib import Path


STATE_FILE = Path(__file__).resolve().parent / "state.json"


def load_state():
    if not STATE_FILE.exists():
        return {
            "articles": {},
            "events": {},
        }

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        state = json.load(file)

    state.setdefault(
        "articles",
        {},
    )

    state.setdefault(
        "events",
        {},
    )

    for event in state["events"].values():
        if "calendar_event_id" in event:
            old_calendar_event_id = event.pop(
                "calendar_event_id"
            )

            if old_calendar_event_id:
                event["calendar_event_ids"] = [
                    old_calendar_event_id
                ]
            else:
                event["calendar_event_ids"] = []

        event.setdefault(
            "calendar_event_ids",
            [],
        )

    return state


def save_state(state):
    with open(
        STATE_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            state,
            file,
            indent=2,
            ensure_ascii=False,
        )


def get_article_id(article):
    return hashlib.sha256(
        article["url"].encode("utf-8")
    ).hexdigest()


def normalize_event_name(event_name):
    normalized = event_name.lower().strip()
    normalized = re.sub(
        r"[^a-z0-9]+",
        " ",
        normalized,
    )
    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )
    return normalized.strip()


def get_event_id(classification):
    event_name = classification.get("event_name")

    if not event_name:
        return None

    normalized_name = normalize_event_name(
        event_name
    )

    return hashlib.sha256(
        normalized_name.encode("utf-8")
    ).hexdigest()


def is_article_known(state, article_id):
    return article_id in state["articles"]


def get_event(state, event_id):
    if not event_id:
        return None

    return state["events"].get(event_id)


def add_article_to_event(
    state,
    article_id,
    event_id,
):
    if not event_id:
        return

    event = state["events"].setdefault(
        event_id,
        {
            "event_name": None,
            "classification": None,
            "article_ids": [],
            "calendar_event_ids": [],
        },
    )

    if article_id not in event["article_ids"]:
        event["article_ids"].append(
            article_id
        )


def update_event(
    state,
    event_id,
    classification,
):
    if not event_id:
        return

    event = state["events"].setdefault(
        event_id,
        {
            "event_name": classification.get(
                "event_name"
            ),
            "classification": None,
            "article_ids": [],
            "calendar_event_ids": [],
        },
    )

    event["event_name"] = classification.get(
        "event_name"
    )

    event["classification"] = classification


def set_calendar_event_ids(
    state,
    event_id,
    calendar_event_ids,
):
    if not event_id:
        return

    event = state["events"].setdefault(
        event_id,
        {
            "event_name": None,
            "classification": None,
            "article_ids": [],
            "calendar_event_ids": [],
        },
    )

    event["calendar_event_ids"] = (
        calendar_event_ids
    )


def get_calendar_event_ids(
    state,
    event_id,
):
    if not event_id:
        return []

    event = state["events"].get(
        event_id
    )

    if not event:
        return []

    return event.get(
        "calendar_event_ids",
        [],
    )


def record_article(
    state,
    article,
    article_id,
    event_id,
    classification=None,
):
    state["articles"][article_id] = {
        "url": article["url"],
        "title": article["title"],
        "published_at": article["published_at"],
        "event_id": event_id,
    }

    if event_id:
        add_article_to_event(
            state,
            article_id,
            event_id,
        )

        if classification:
            update_event(
                state,
                event_id,
                classification,
            )