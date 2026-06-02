import requests

from ..base import Scraper

SEARCH_API_URL = "https://www.marktplaats.nl/lrp/api/search"
LISTING_BASE_URL = "https://www.marktplaats.nl"
OSRM_TABLE_URL = "http://router.project-osrm.org/table/v1/driving/{coords}?sources=0&annotations=duration"
RESULTS_PER_REQUEST = 30
REQUEST_TIMEOUT_SECONDS = 20

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

# Emmeloord (lon, lat) — OSRM uses longitude first.
_EMMELOORD = (5.75, 52.7167)


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
        raw_listings = self._fetch_raw()
        drive_times = self._batch_drive_times(raw_listings)
        return [
            self._parse(item, drive_times.get(i, ""))
            for i, item in enumerate(raw_listings)
            if item.get("itemId")
        ]

    def _fetch_raw(self) -> list[dict]:
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
        return response.json().get("listings", [])

    def _batch_drive_times(self, raw_listings: list[dict]) -> dict[int, str]:
        """One OSRM Table request: Emmeloord → all listings with known coordinates."""
        coords = [_EMMELOORD]
        coord_to_listing: dict[int, int] = {}  # coord index → listing index

        for i, item in enumerate(raw_listings):
            loc = item.get("location") or {}
            lat, lon = loc.get("latitude"), loc.get("longitude")
            if lat and lon and not loc.get("onCountryLevel"):
                coord_to_listing[len(coords)] = i
                coords.append((lon, lat))

        if len(coords) == 1:
            return {}

        coord_str = ";".join(f"{lon},{lat}" for lon, lat in coords)
        try:
            response = requests.get(
                OSRM_TABLE_URL.format(coords=coord_str), timeout=self.timeout
            )
            response.raise_for_status()
            durations = response.json().get("durations", [[]])[0]
        except Exception:
            return {}

        result = {}
        for coord_idx, listing_idx in coord_to_listing.items():
            seconds = durations[coord_idx] if coord_idx < len(durations) else None
            if seconds is not None:
                result[listing_idx] = _seconds_to_drive_str(int(seconds))
        return result

    def _parse(self, raw: dict, drive_time: str = "") -> dict:
        relative_url = raw.get("vipUrl") or raw.get("url") or ""
        url = relative_url if relative_url.startswith("http") else LISTING_BASE_URL + relative_url

        loc = raw.get("location") or {}
        attrs = {a["key"]: a.get("value", "") for a in (raw.get("attributes") or [])}

        return {
            "id": str(raw.get("itemId", "")).strip(),
            "title": (raw.get("title") or "Geen titel").strip(),
            "price": _format_price(raw.get("priceInfo") or {}),
            "url": url,
            "city": loc.get("cityName") or "",
            "drive_time": drive_time,
            "condition": attrs.get("condition", ""),
            "delivery": attrs.get("delivery", ""),
            "date": raw.get("date", ""),
            "seller": (raw.get("sellerInformation") or {}).get("sellerName", ""),
        }


def _format_price(price_info: dict) -> str:
    price_type = price_info.get("priceType", "")
    cents = price_info.get("priceCents")
    if isinstance(cents, int):
        amount = f"€{cents / 100:.2f}".replace(".", ",")
        if price_type == "MIN_BID":
            return f"{amount} (min. bod)"
        if price_type == "FIXED":
            return amount
    return PRICE_TYPE_LABELS.get(price_type, "Prijs onbekend")


def _seconds_to_drive_str(seconds: int) -> str:
    minutes = round(seconds / 60 / 5) * 5  # round to nearest 5 min
    if minutes < 60:
        return f"~{minutes} min"
    hours, mins = divmod(minutes, 60)
    return f"~{hours}u {mins}min" if mins else f"~{hours}u"
