import requests

from ..base import Notifier

REQUEST_TIMEOUT_SECONDS = 20


class NtfyNotifier(Notifier):
    def __init__(
        self,
        topic: str,
        server: str = "https://ntfy.sh",
        title: str = "Nieuwe aanbieding!",
        tags: str = "bell",
        priority: str = "high",
        timeout: int = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        self.url = f"{server.rstrip('/')}/{topic}"
        self.title = title
        self.tags = tags
        self.priority = priority
        self.timeout = timeout

    def send(self, listing: dict) -> None:
        body = f"{listing['title']}\n{listing['price']}"
        headers = {
            "Title": self.title,
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
