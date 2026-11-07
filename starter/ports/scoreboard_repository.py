"""Repository for persisting and retrieving Sudoku game scores."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Type alias for score entries (name, time, difficulty, hints, date)
ScoreEntry = tuple[str, int, str, int, str]


class ScoreboardRepository:
    """Manage persistent storage of game scores to JSON file."""

    def __init__(self, data_dir: str = "data", filename: str = "scoreboard_data.json") -> None:
        """Initialize the scoreboard repository.

        Args:
            data_dir: Directory to store scoreboard data (will be created if needed)
            filename: Name of the JSON file to store scores
        """
        self.data_dir = Path(data_dir)
        self.filepath = self.data_dir / filename
        self.scores: list[ScoreEntry] = []
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """Ensure the data directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        """Load scores from the JSON file."""
        if not self.filepath.exists():
            self.scores = []
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.scores = []
            if isinstance(data, list):
                for entry in data:
                    if self._is_valid_entry(entry):
                        self.scores.append(
                            (
                                str(entry["name"]),
                                int(entry["time"]),
                                str(entry["difficulty"]),
                                int(entry["hints"]),
                                str(entry["date"]),
                            )
                        )

            # Sort by time (ascending) to maintain top scores by speed
            self.scores.sort(key=lambda s: s[1])
        except (json.JSONDecodeError, TypeError, ValueError, IOError):
            self.scores = []

    def save(self) -> None:
        """Save scores to the JSON file."""
        self._ensure_data_dir()

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

        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"Failed to save scoreboard: {e}")

    def add_score(
        self, name: str, time: int, difficulty: str, hints: int, date: str
    ) -> None:
        """Add a new score to the scoreboard.

        Args:
            name: Player name (will be validated)
            time: Time taken in seconds
            difficulty: Difficulty level (e.g., 'easy', 'medium', 'hard')
            hints: Number of hints used
            date: ISO format date string

        Raises:
            ValueError: If input validation fails
        """
        name_clean = name.strip()
        if len(name_clean) < 1 or len(name_clean) > 30:
            raise ValueError("Name must be 1-30 characters.")
        if not isinstance(time, int) or time < 0:
            raise ValueError("Time must be a non-negative integer.")
        if not isinstance(difficulty, str) or not difficulty:
            raise ValueError("Difficulty must be a non-empty string.")
        if not isinstance(hints, int) or hints < 0:
            raise ValueError("Hints must be a non-negative integer.")

        entry: ScoreEntry = (name_clean, time, difficulty, hints, date)
        self.scores.append(entry)
        self.scores.sort(key=lambda s: s[1])

    def get_top_scores(self, limit: int = 10) -> list[ScoreEntry]:
        """Get the top scores by time.

        Args:
            limit: Maximum number of scores to return

        Returns:
            List of top score entries
        """
        return self.scores[:limit]

    @staticmethod
    def _is_valid_entry(entry: Any) -> bool:
        """Validate a score entry object."""
        return (
            isinstance(entry, dict)
            and isinstance(entry.get("name"), str)
            and isinstance(entry.get("difficulty"), str)
            and isinstance(entry.get("date"), str)
            and isinstance(entry.get("time"), int)
            and isinstance(entry.get("hints"), int)
        )
