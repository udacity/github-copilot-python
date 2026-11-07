"""Application configuration constants."""

from typing import Dict, Tuple

# Difficulty levels for Sudoku puzzle generation
DIFFICULTY_RANGES: Dict[str, Tuple[int, int]] = {
    "easy": (40, 45),
    "medium": (30, 35),
    "hard": (25, 28),
}

