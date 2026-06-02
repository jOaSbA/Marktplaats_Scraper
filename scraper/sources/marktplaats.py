import requests

from ..base import Scraper

SEARCH_API_URL = "https://www.marktplaats.nl/lrp/api/search"
LISTING_BASE_URL = "https://www.marktplaats.nl"
RESULTS_PER_REQUEST = 30
REQUEST_TIMEOUT_SECONDS = 20

# The API answers with 403 for the default requests User-Agent.
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

PRICE_TYPE_LABELS = {
    "BIDDING": "Bieden",
    "FREE": "Gratis",
    "RESERVED": "Gereserveerd",
    "SEE_DESCRIPTION": "Zie omschrijving",
    "NOTK": "n.o.t.k.",
}


class MarktplaatsScraper(Scraper):
    def __init__(
        self,
        query: str,
        limit: int = RESULTS_PER_REQUEST,
        timeout: int = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        self.query = query
        self.limit = limit
        self.timeout = timeout

    def fetch(self) -> list[dict]:
        params = {"query": self.query, "limit": self.limit, "offset": 0}
        headers = {
            "User-Agent": BROWSER_USER_AGENT,
            "Accept": "application/json",
            "Accept-Encoding": "identity",
        }
        response = requests.get(
            SEARCH_API_URL, params=params, headers=headers, timeout=self.timeout
        )
        response.raise_for_status()
        raw_listings = response.json().get("listings", [])
        return [self._parse(item) for item in raw_listings if item.get("itemId")]

    def _parse(self, raw: dict) -> dict:
        relative_url = raw.get("vipUrl") or raw.get("url") or ""
        url = relative_url if relative_url.startswith("http") else LISTING_BASE_URL + relative_url
        return {
            "id": str(raw.get("itemId", "")).strip(),
            "title": (raw.get("title") or "Geen titel").strip(),
            "price": self._format_price(raw.get("priceInfo")),
            "url": url,
        }

    def _format_price(self, price_info: dict | None) -> str:
        price_info = price_info or {}
        price_type = price_info.get("priceType", "")
        cents = price_info.get("priceCents")
        if price_type in ("FIXED", "MIN_BID") and isinstance(cents, int):
            return f"€{cents / 100:.2f}".replace(".", ",")
        return PRICE_TYPE_LABELS.get(price_type, "Prijs onbekend")
