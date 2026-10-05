import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


NEWS_URL = "https://pokemongolive.com/news/"

EXCLUDED_URLS = {
    "https://pokemongolive.com/news/#main",
}


def get_news_articles():
    response = requests.get(
        NEWS_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Pokémon GO Calendar Automation)"
        },
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    print(f"Downloaded {len(response.text):,} bytes")
    print()

    links = soup.find_all("a", href=True)

    seen = set()
    articles = []

    for link in links:
        href = urljoin(NEWS_URL, link["href"])
        text = link.get_text(" ", strip=True)

        if href in EXCLUDED_URLS:
            continue

        if "/news/" not in href:
            continue

        if not text:
            continue

        if href in seen:
            continue

        seen.add(href)

        article = {
            "title": text,
            "url": href,
            "published_at": None,
        }

        articles.append(article)

    return articles


if __name__ == "__main__":
    articles = get_news_articles()

    print(f"Found {len(articles)} potential news links:")
    print()

    for article in articles[:30]:
        print(f"TITLE:     {article['title']}")
        print(f"URL:       {article['url']}")
        print(f"PUBLISHED: {article['published_at']}")
        print("-" * 80)