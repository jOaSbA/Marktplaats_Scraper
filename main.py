#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from scraper.engine import Engine
from scraper.notifiers.ntfy import NtfyNotifier
from scraper.sources.marktplaats import MarktplaatsScraper
from scraper.stores.json_store import JsonSeenStore

NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
if not NTFY_TOPIC:
    sys.exit("NTFY_TOPIC is not set. Add it as a secret or environment variable.")

SEARCH_QUERY = os.environ.get("SEARCH_QUERY")
if not SEARCH_QUERY:
    sys.exit("SEARCH_QUERY is not set. Add it as a repository variable or environment variable.")

scraper = MarktplaatsScraper(query=SEARCH_QUERY)

notifier = NtfyNotifier(
    topic=NTFY_TOPIC,
    server=os.environ.get("NTFY_SERVER", "https://ntfy.sh"),
    tags=os.environ.get("NTFY_TAGS") or "bell",
)

store = JsonSeenStore(
    path=Path(os.environ.get("SEEN_FILE", "seen.json")),
)

try:
    Engine(scraper, notifier, store, query=SEARCH_QUERY).run()
except Exception as exc:
    print(f"Run failed: {exc}")
    try:
        notifier.send_error(str(exc))
    except Exception as notify_exc:
        print(f"Also failed to send error notification: {notify_exc}")
