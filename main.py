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

scraper = MarktplaatsScraper(
    query=os.environ.get("SEARCH_QUERY", "ninja creami"),
)

notifier = NtfyNotifier(
    topic=NTFY_TOPIC,
    server=os.environ.get("NTFY_SERVER", "https://ntfy.sh"),
    title=os.environ.get("NTFY_TITLE", "Nieuwe aanbieding!"),
    tags=os.environ.get("NTFY_TAGS", "bell"),
)

store = JsonSeenStore(
    path=Path(os.environ.get("SEEN_FILE", "seen.json")),
)

Engine(scraper, notifier, store).run()
