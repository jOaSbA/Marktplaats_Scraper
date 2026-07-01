import base64

import requests

from ..base import Notifier

REQUEST_TIMEOUT_SECONDS = 20


def _encode_header(value: str) -> str:
    """RFC 2047 encoded-word, since HTTP headers are Latin-1 only but ntfy
    decodes this form as UTF-8 (needed for things like the euro sign)."""
    encoded = base64.b64encode(value.encode("utf-8")).decode("ascii")
    return f"=?UTF-8?B?{encoded}?="


class NtfyNotifier(Notifier):
    def __init__(
        self,
        topic: str,
        server: str = "https://ntfy.sh",
        tags: str = "bell",
        priority: str = "high",
        timeout: int = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        self.url = f"{server.rstrip('/')}/{topic}"
        self.tags = tags
        self.priority = priority
        self.timeout = timeout

    def send(self, listing: dict) -> None:
        title = f"{listing['title']} | {listing['price']}"

        lines = []
        location_parts = [p for p in [listing.get("city"), listing.get("drive_time")] if p]
        if location_parts:
            lines.append("📍 " + " · ".join(location_parts))

        detail_parts = [p for p in [listing.get("condition"), listing.get("delivery")] if p]
        if detail_parts:
            lines.append("🔧 " + " · ".join(detail_parts))

        if listing.get("date"):
            lines.append(f"📅 {listing['date']}")

        body = "\n".join(lines) if lines else title

        headers = {
            "Title": _encode_header(title),
            "Tags": self.tags,
            "Click": listing["url"],
            "Priority": self.priority,
        }
        response = requests.post(
            self.url,
            data=body.encode("utf-8"),
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()

    def send_error(self, message: str) -> None:
        headers = {
            "Title": "Marktplaats watch error",
            "Tags": "warning",
            "Priority": "default",
        }
        response = requests.post(
            self.url,
            data=message.encode("utf-8", errors="replace"),
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
