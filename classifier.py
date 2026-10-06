import json
import sys

import requests
from bs4 import BeautifulSoup

from classifier_prompt import build_prompt


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3.5:9b"


def get_urls(args):
    urls = []

    for arg in args:
        if arg.startswith("http://") or arg.startswith("https://"):
            urls.append(arg)
            continue

        with open(arg, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                urls.append(line)

    return urls


def fetch_article(url):
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Pokémon GO Calendar Automation)"
        },
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup.select(
        "header, nav, footer, aside, script, style, noscript"
    ):
        element.decompose()

    article = soup.find("article")

    if article is None:
        raise ValueError(
            f"Could not find article content on {url}"
        )

    return article.get_text(
        "\n",
        strip=True,
    )


def classify_article(article_text):
    prompt = build_prompt(article_text)

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
        "format": "json",
        "think": True,
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

    return json.loads(content)


def validate_result(result):
    required_fields = [
        "announcement_type",
        "primary_subject",
        "event_types",
        "event_name",
        "start",
        "end",
        "event_periods",
        "timezone",
        "locations",
        "is_update",
        "is_cancellation",
        "details",
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(
                f"Missing required field: {field}"
            )

    if result["announcement_type"] not in {
        "new_event",
        "event_update",
        "event_reschedule",
        "event_cancellation",
        "information",
    }:
        raise ValueError(
            f"Invalid announcement_type: "
            f"{result['announcement_type']}"
        )

    if not isinstance(result["event_types"], list):
        raise ValueError(
            "event_types must be a list"
        )

    if not isinstance(result["locations"], list):
        raise ValueError(
            "locations must be a list"
        )

    if result["start"] is not None:
        if not isinstance(result["start"], str):
            raise ValueError(
                "start must be a string or null"
            )

    if result["end"] is not None:
        if not isinstance(result["end"], str):
            raise ValueError(
                "end must be a string or null"
            )

    event_periods = result["event_periods"]

    if not isinstance(event_periods, list):
        raise ValueError(
            "event_periods must be a list"
        )

    for period in event_periods:
        if not isinstance(period, dict):
            raise ValueError(
                "Each event_period must be an object"
            )

        if not period.get("start"):
            raise ValueError(
                "Each event_period must have a start"
            )

        if not period.get("end"):
            raise ValueError(
                "Each event_period must have an end"
            )

        if not period.get("label"):
            raise ValueError(
                "Each event_period must have a label"
            )

    details = result["details"]

    if not isinstance(details, dict):
        raise ValueError(
            "details must be an object"
        )

    watch_requirements = details.get(
        "watch_requirements_minutes",
        [],
    )

    if not isinstance(watch_requirements, list):
        raise ValueError(
            "watch_requirements_minutes must be a list"
        )

    if result["event_types"] == ["twitch_drops"]:
        if result["end"] is not None:
            raise ValueError(
                "Twitch Drops must have end = null"
            )

        if not details.get("is_online"):
            raise ValueError(
                "Twitch Drops must have is_online = true"
            )

        if not watch_requirements:
            raise ValueError(
                "Twitch Drops must have watch requirements"
            )


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: py classifier.py <url> [url ...]"
        )
        print(
            "   or: py classifier.py <url_list.txt>"
        )
        sys.exit(1)

    urls = get_urls(sys.argv[1:])

    for index, url in enumerate(urls, start=1):
        print("=" * 80)
        print(f"ARTICLE {index}/{len(urls)}")
        print("=" * 80)
        print(f"URL: {url}")
        print()

        try:
            article_text = fetch_article(
                url
            )

            print(
                f"Extracted {len(article_text):,} "
                "characters of article text."
            )
            print()

            result = classify_article(
                article_text
            )
            validate_result(result)

            print(
                json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False,
                )
            )

        except Exception as exc:
            print(f"ERROR: {exc}")

        print()


if __name__ == "__main__":
    main()
