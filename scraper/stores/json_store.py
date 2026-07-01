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

    def _load_state(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            return {}
        if isinstance(data, list):
            # Old format: a plain list of IDs with no query attached.
            return {"query": None, "ids": data}
        return data

    def load(self) -> set[str]:
        return set(self._load_state().get("ids", []))

    def load_query(self) -> str | None:
        return self._load_state().get("query")

    def save(self, ids: list[str], query: str) -> None:
        self.path.write_text(
            json.dumps({"query": query, "ids": ids[: self.max_ids]}, indent=2),
            encoding="utf-8",
        )
