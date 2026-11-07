"""In-memory puzzle store adapter.

Implements the PuzzleRepositoryPort using an in-memory dictionary.
Suitable for development and testing, not production use.
"""

import uuid
from typing import Dict, List, Optional

from domain.puzzle import Puzzle
from starter.ports.puzzle_repository import PuzzleRepositoryPort


class MemoryPuzzleStore(PuzzleRepositoryPort):
    """In-memory implementation of puzzle persistence.

    Stores puzzles in a dictionary during the application lifetime.
    Data is lost when the application terminates.
    """

    def __init__(self) -> None:
        """Initialize the in-memory store."""
        self._puzzles: Dict[str, Puzzle] = {}

    def save_puzzle(self, puzzle: Puzzle) -> None:
        """Save a puzzle to memory.

        Args:
            puzzle: The puzzle to save
        """
        puzzle_id = str(uuid.uuid4())
        self._puzzles[puzzle_id] = puzzle

    def get_puzzle(self, puzzle_id: str) -> Optional[Puzzle]:
        """Retrieve a puzzle by ID.

        Args:
            puzzle_id: The puzzle identifier

        Returns:
            The puzzle or None if not found.
        """
        return self._puzzles.get(puzzle_id)

    def list_puzzles(self) -> List[Puzzle]:
        """List all stored puzzles.

        Returns:
            A list of all puzzles in the store.
        """
        return list(self._puzzles.values())

    def delete_puzzle(self, puzzle_id: str) -> bool:
        """Delete a puzzle from the store.

        Args:
            puzzle_id: The puzzle to delete

        Returns:
            True if deleted, False if not found.
        """
        if puzzle_id in self._puzzles:
            del self._puzzles[puzzle_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all puzzles from the store.

        Useful for testing.
        """
        self._puzzles.clear()
