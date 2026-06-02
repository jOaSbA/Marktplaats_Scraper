import json
from pathlib import Path

from ..base import SeenStore

MAX_REMEMBERED_IDS = 300


class JsonSeenStore(SeenStore):
    def __init__(self, path: Path = Path("seen.json"), max_ids: int = MAX_REMEMBERED_IDS) -> None:
        self.path = path
        self.max_ids = max_ids

    def exists(self) -> bool:
        return self.path.exists()

    def load(self) -> set[str]:
        if not self.path.exists():
            return set()
        try:
            return set(json.loads(self.path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, ValueError):
            return set()

    def save(self, ids: list[str]) -> None:
        self.path.write_text(
            json.dumps(ids[: self.max_ids], indent=2),
            encoding="utf-8",
        )
