from abc import ABC, abstractmethod


class Scraper(ABC):
    @abstractmethod
    def fetch(self) -> list[dict]:
        """Return a list of listings, each a dict with keys: id, title, price, url."""


class Notifier(ABC):
    @abstractmethod
    def send(self, listing: dict) -> None:
        """Send an alert for a single new listing."""


class SeenStore(ABC):
    @abstractmethod
    def exists(self) -> bool:
        """Return True if the store has been initialised (i.e. not a first run)."""

    @abstractmethod
    def load(self) -> set[str]:
        """Return the set of listing IDs already notified about."""

    @abstractmethod
    def save(self, ids: list[str]) -> None:
        """Persist the ordered list of listing IDs."""
