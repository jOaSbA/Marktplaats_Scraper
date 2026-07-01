from .base import Notifier, Scraper, SeenStore


class Engine:
    def __init__(self, scraper: Scraper, notifier: Notifier, store: SeenStore, query: str) -> None:
        self.scraper = scraper
        self.notifier = notifier
        self.store = store
        self.query = query

    def run(self) -> None:
        is_first_run = not self.store.exists() or self.store.load_query() != self.query
        if is_first_run and self.store.exists():
            print("Search query changed since the last run: reseeding without notifying.")

        listings = self.scraper.fetch()
        if not listings:
            print("No listings returned. The API response format may have changed.")
            return

        current_ids = [item["id"] for item in listings]

        if is_first_run:
            print(f"First run: remembering {len(current_ids)} listings without notifying.")
            self.store.save(current_ids, self.query)
            return

        seen_ids = self.store.load()
        new_listings = [item for item in listings if item["id"] not in seen_ids]

        for listing in new_listings:
            print(f"New listing: {listing['title']} ({listing['price']})")
            self.notifier.send(listing)

        if not new_listings:
            print("No new listings this run.")

        leftover_ids = [id_ for id_ in seen_ids if id_ not in current_ids]
        self.store.save(current_ids + leftover_ids, self.query)
