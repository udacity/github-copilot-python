"""Scoreboard data model and persistence utilities."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

ScoreEntry = Tuple[str, int, str, int, str]


class Scoreboard:
    """Manage game score entries and persistence."""

    STORAGE_KEY = "sudokuScoreboard"
    FALLBACK_FILENAME = "scoreboard_storage.json"

    def __init__(self, max_entries: int = 10) -> None:
        self.max_entries = max_entries
        self.scores: List[ScoreEntry] = []

    def add_score(self, name: str, time: int, difficulty: str, hints: int) -> None:
        """Add a new score and maintain the top scores."""
        name_clean = name.strip()
        if len(name_clean) < 1 or len(name_clean) > 30:
            raise ValueError("Name must be 1-30 characters.")
        if not isinstance(time, int) or time < 0:
            raise ValueError("Time must be a non-negative integer.")
        if not isinstance(difficulty, str) or not difficulty:
            raise ValueError("Difficulty must be a non-empty string.")
        if not isinstance(hints, int) or hints < 0:
            raise ValueError("Hints must be a non-negative integer.")

        entry: ScoreEntry = (
            name_clean,
            time,
            difficulty,
            hints,
            datetime.utcnow().isoformat(),
        )
        self.scores.append(entry)
        self.scores.sort(key=lambda score: score[1])
        self.scores = self.scores[: self.max_entries]

    def get_top_10(self) -> List[ScoreEntry]:
        """Return the top 10 scores."""
        return list(self.scores)

    def save_to_localStorage(self, storage: Optional[Any] = None) -> None:
        """Persist scoreboard entries to localStorage or a fallback file."""
        payload = [
            {
                "name": name,
                "time": time,
                "difficulty": difficulty,
                "hints": hints,
                "date": date,
            }
            for name, time, difficulty, hints, date in self.scores
        ]
        serialized = json.dumps(payload)

        if storage is not None and hasattr(storage, "setItem"):
            storage.setItem(self.STORAGE_KEY, serialized)
            return

        with open(self.FALLBACK_FILENAME, "w", encoding="utf-8") as handler:
            handler.write(serialized)

    def load_from_localStorage(self, storage: Optional[Any] = None) -> None:
        """Load scoreboard entries from localStorage or a fallback file."""
        raw = None
        if storage is not None and hasattr(storage, "getItem"):
            raw = storage.getItem(self.STORAGE_KEY)
        else:
            try:
                with open(self.FALLBACK_FILENAME, "r", encoding="utf-8") as handler:
                    raw = handler.read()
            except FileNotFoundError:
                raw = None

        if not raw:
            self.scores = []
            return

        try:
            data = json.loads(raw)
            self.scores = [
                (
                    str(entry["name"]),
                    int(entry["time"]),
                    str(entry["difficulty"]),
                    int(entry["hints"]),
                    str(entry["date"]),
                )
                for entry in data
                if self._is_valid_entry(entry)
            ]
            self.scores.sort(key=lambda score: score[1])
            self.scores = self.scores[: self.max_entries]
        except (TypeError, ValueError, json.JSONDecodeError):
            self.scores = []

    @staticmethod
    def _is_valid_entry(entry: Any) -> bool:
        return (
            isinstance(entry, dict)
            and isinstance(entry.get("name"), str)
            and isinstance(entry.get("difficulty"), str)
            and isinstance(entry.get("date"), str)
            and isinstance(entry.get("time"), int)
            and isinstance(entry.get("hints"), int)
        )
