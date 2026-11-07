"""Port (interface) for game service operations.

Defines the contract that any game service implementation must follow.
"""

from abc import ABC, abstractmethod
from typing import Any

from domain.puzzle import Puzzle


class GameServicePort(ABC):
    """Abstract port for game service operations.

    This interface defines all operations the game service must support,
    allowing different implementations to be swapped in.
    """

    @abstractmethod
    def new_game(self, difficulty: str = "medium", clues: int | None = None) -> list[list[int]]:
        """Start a new game by generating a puzzle.

        Args:
            clues: Number of clues for the puzzle.

        Returns:
            The puzzle grid with clues visible.
        """
        pass

    @abstractmethod
    def check_solution(self, board: list[list[int]]) -> tuple[list[list[int]], bool]:
        """Check a board against the current solution.

        Args:
            board: The board to check

        Returns:
            A tuple of (incorrect_cells, is_complete)
        """
        pass

    @abstractmethod
    def get_current_puzzle(self) -> Puzzle | None:
        """Get the current puzzle if one is in progress.

        Returns:
            The current Puzzle object or None.
        """
        pass

    @abstractmethod
    def has_active_game(self) -> bool:
        """Check if a game is currently in progress.

        Returns:
            True if a puzzle is loaded, False otherwise.
        """
        pass

    @abstractmethod
    def hint(self, board: list[list[int]] | None = None) -> dict[str, Any]:
        """Provide a hint by filling one empty cell."""
        pass

    @abstractmethod
    def get_locked_cells(self) -> list[dict[str, int]]:
        """Return the current locked-cell positions."""
        pass

    @abstractmethod
    def get_game_stats(self) -> dict[str, Any]:
        """Return the current game statistics."""
        pass

    @abstractmethod
    def reset_game(self) -> None:
        """Clear the current puzzle and reset game state."""
        pass
