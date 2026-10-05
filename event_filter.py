import json
from datetime import datetime

import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3.5:9b"


FILTER_SCHEMA = {
    "type": "object",
    "properties": {
        "event_end": {
            "type": ["string", "null"],
            "description": (
                "The date and time when the event completely ends, "
                "in YYYY-MM-DDTHH:MM:SS format. "
                "Return null if the article does not provide enough "
                "information to determine the event end."
            ),
        }
    },
    "required": ["event_end"],
}


def build_filter_prompt(article_text):
    return f"""
Extract the END date and time of the primary Pokémon GO event
described in this article.

Your ONLY job is to identify when the event completely ends.
Do not determine whether it has already ended.
Do not compare dates.
Do not perform date arithmetic.

Rules:

1. Return the event's FINAL end date and time.
2. For multi-day events, return the end of the final day.
3. If the event has a start and end time, return the end time.
4. If only an end date is provided, use that date at 23:59:59.
5. If the event occurs over multiple days and only dates are provided,
   use 23:59:59 on the final day.
6. If the article describes a rescheduled event, use the CURRENT
   rescheduled end date/time.
7. Ignore dates belonging to unrelated events mentioned in the article.
8. Ignore the article's publication date.
9. If the article does not provide enough information to determine
   when the event ends, return null.
10. Return the date/time in exactly this format:

YYYY-MM-DDTHH:MM:SS

Examples:

Event:
"Community Day takes place October 10-11, 2026, from 2:00 PM
to 5:00 PM local time each day."

Return:
{{
  "event_end": "2026-10-11T17:00:00"
}}

Event:
"The event runs October 5, 2026, from 10:00 AM to 10:00 PM."

Return:
{{
  "event_end": "2026-10-05T22:00:00"
}}

Event:
"GO Tour 2027 has been announced. More details will be revealed later."

Return:
{{
  "event_end": null
}}

Return ONLY JSON matching this schema:

{json.dumps(FILTER_SCHEMA, indent=2)}

ARTICLE:
{article_text}
""".strip()


def extract_event_end(article_text):
    prompt = build_filter_prompt(
        article_text
    )

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
        "format": FILTER_SCHEMA,
        "think": False,
        "keep_alive": "30s",
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120,
    )
    response.raise_for_status()

    data = response.json()
    content = data["message"]["content"]

    result = json.loads(content)

    event_end = result.get("event_end")

    if event_end is None:
        return None

    try:
        return datetime.fromisoformat(
            event_end
        )
    except ValueError as exc:
        raise ValueError(
            f"Invalid event_end returned by LLM: {event_end!r}"
        ) from exc


def event_has_ended(
    article_text,
    current_datetime=None,
):
    if current_datetime is None:
        current_datetime = datetime.now()

    event_end = extract_event_end(
        article_text
    )

    if event_end is None:
        return False

    return event_end < current_datetime