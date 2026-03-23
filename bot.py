import os
import json
import re
import feedparser
import requests

RSS_URL = "https://www.diariocoimbra.pt/feed/"
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
SEEN_FILE = "seen.json"


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def send_message(text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
        timeout=10,
    )


def format_message(entry):
    title = entry.get("title", "").strip()
    link = entry.get("link", "").strip()
    summary = re.sub(r"<[^>]+>", "", entry.get("summary", "")).strip()
    if len(summary) > 300:
        summary = summary[:300] + "..."
    text = f"📰 <b>{title}</b>"
    if summary:
        text += f"\n\n{summary}"
    text += f"\n\n🔗 <a href='{link}'>Ler mais</a>"
    return text


def main():
    seen = load_seen()
    articles = feedparser.parse(RSS_URL).entries
    sent = 0

    for entry in articles:
        entry_id = entry.get("id") or entry.get("link")
        if entry_id in seen:
            continue
        send_message(format_message(entry))
        seen.add(entry_id)
        sent += 1

    save_seen(seen)
    print(f"Sent {sent} new articles.")


if __name__ == "__main__":
    main()
