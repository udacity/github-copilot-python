"""Data model for Sudoku game state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

@dataclass
class GameState:
    """Represents the current state of a Sudoku game."""

    board: List[List[int]] = field(default_factory=lambda: [[0 for _ in range(9)] for _ in range(9)])
    difficulty: str = "medium"
    start_time: Optional[datetime] = None
    hints_used: int = 0
    locked_cells: List[CellPosition] = field(default_factory=list)
    is_complete: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize game state to a JSON-friendly dictionary."""
        return {
            "board": [row.copy() for row in self.board],
            "difficulty": self.difficulty,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "hints_used": self.hints_used,
            "locked_cells": [cell.copy() for cell in self.locked_cells],
            "is_complete": self.is_complete,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        """Restore a GameState instance from a dictionary."""
        start_time = data.get("start_time")
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)

        return cls(
            board=[row.copy() for row in data.get("board", [[0] * 9 for _ in range(9)])],
            difficulty=data.get("difficulty", "medium"),
            start_time=start_time,
            hints_used=int(data.get("hints_used", 0)),
            locked_cells=[cell.copy() for cell in data.get("locked_cells", [])],
            is_complete=bool(data.get("is_complete", False)),
        )
