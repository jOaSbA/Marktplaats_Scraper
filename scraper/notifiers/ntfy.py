import requests

from ..base import Notifier

REQUEST_TIMEOUT_SECONDS = 20


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
        title = f"{listing['title']} — {listing['price']}"

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
            "Title": title,
            "Tags": self.tags,
            "Click": listing.get("mobile_url") or listing["url"],
            "Priority": self.priority,
        }
        response = requests.post(
            self.url,
            data=body.encode("utf-8"),
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
