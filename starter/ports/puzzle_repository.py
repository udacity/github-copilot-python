"""Port (interface) for puzzle repository persistence.

Defines the contract for storing and retrieving puzzles.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.puzzle import Puzzle


class PuzzleRepositoryPort(ABC):
    """Abstract port for puzzle persistence.

    This interface allows different storage backends (memory, database, etc.)
    to be implemented and swapped as needed.
    """

    @abstractmethod
    def save_puzzle(self, puzzle: Puzzle) -> None:
        """Save a puzzle to storage.

        Args:
            puzzle: The puzzle to save
        """
        pass

    @abstractmethod
    def get_puzzle(self, puzzle_id: str) -> Optional[Puzzle]:
        """Retrieve a puzzle by ID.

        Args:
            puzzle_id: The unique puzzle identifier

        Returns:
            The puzzle or None if not found.
        """
        pass

    @abstractmethod
    def list_puzzles(self) -> List[Puzzle]:
        """List all stored puzzles.

        Returns:
            A list of all puzzles in storage.
        """
        pass

    @abstractmethod
    def delete_puzzle(self, puzzle_id: str) -> bool:
        """Delete a puzzle from storage.

        Args:
            puzzle_id: The puzzle to delete

        Returns:
            True if deleted, False if not found.
        """
        pass
