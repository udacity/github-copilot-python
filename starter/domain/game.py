"""Core game service implementation.

This module provides the main game service that orchestrates
puzzle generation, state management, and solution checking.
"""

from __future__ import annotations

import os
import random
import sys
import time
from typing import List, Optional, Tuple

# Add the repository root to sys.path to enable imports from sibling packages
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from domain.board import SudokuBoard
from domain.puzzle import Puzzle, PuzzleGenerator
from utils.generation import SudokuGenerator


class GameService:
    """Service for managing Sudoku game operations.

    This is the core service that handles puzzle generation,
    solution verification, and game state management.
    """

    def __init__(self) -> None:
        """Initialize the game service."""
        self._current_puzzle: Optional[Puzzle] = None
        self._locked_cells: list[dict[str, int]] = []
        self._locked_cell_positions: set[tuple[int, int]] = set()
        self._game_start_time: Optional[float] = None
        self._current_difficulty: Optional[str] = None
        self._hints_used: int = 0

    def new_game(self, difficulty: str = "medium", clues: int | None = None) -> list[list[int]]:
        """Start a new game by generating a puzzle.

        Args:
            difficulty: Difficulty level ('easy', 'medium', 'hard'). Default is 'medium'.
            clues: Exact number of clues, if provided.

        Returns:
            The puzzle grid with clues visible.

        Raises:
            ValueError: If difficulty or clues are not valid.
        """
        self._game_start_time = time.time()
        self._current_difficulty = difficulty if clues is None else "custom"
        self._hints_used = 0

        if clues is not None:
            self._current_puzzle = PuzzleGenerator.generate(clues=clues)
        else:
            puzzle, solution = SudokuGenerator.generate_puzzle(difficulty=difficulty)
            self._current_puzzle = Puzzle(puzzle, solution, sum(1 for row in puzzle for cell in row if cell != 0))

        self._locked_cells, self._locked_cell_positions = self._build_locked_cell_cache(
            self._current_puzzle.puzzle
        )
        return self._current_puzzle.puzzle

    def check_solution(self, board: List[List[int]]) -> tuple[List[List[int]], bool]:
        """Check a board against the current solution.

        Args:
            board: The board to check

        Returns:
            A tuple of (incorrect_cells, is_complete) where:
            - incorrect_cells: List of [row, col] for incorrect cells
            - is_complete: True if puzzle is completely and correctly solved

        Raises:
            RuntimeError: If no game is in progress.
            ValueError: If locked cells have been modified.
        """
        if self._current_puzzle is None:
            raise RuntimeError("No game in progress")

        for locked_cell in self._locked_cells:
            row, col = locked_cell["row"], locked_cell["col"]
            original_value = self._current_puzzle.puzzle[row][col]
            current_value = board[row][col]

            if original_value != 0 and current_value != 0 and current_value != original_value:
                raise ValueError(f"Locked cell at ({row}, {col}) cannot be modified")

        incorrect = [
            [row, col]
            for row in range(9)
            for col in range(9)
            if board[row][col] != self._current_puzzle.solution[row][col]
        ]

        is_complete = not incorrect and SudokuBoard.is_complete(board)
        return incorrect, is_complete

    def get_current_puzzle(self) -> Optional[Puzzle]:
        """Get the current puzzle if one is in progress.

        Returns:
            The current Puzzle object or None if no game is in progress.
        """
        return self._current_puzzle

    def hint(self, board: Optional[list[list[int]]] = None) -> dict:
        """Provide a hint by filling one random empty cell.

        Args:
            board: Optional board state from the client to identify already filled cells.

        Returns:
            A dictionary containing the hint cell position and value.

        Raises:
            RuntimeError: If no game is in progress.
            ValueError: If there are no empty cells available.
        """
        if self._current_puzzle is None:
            raise RuntimeError("No game in progress")

        source_board = board if board is not None else self._current_puzzle.puzzle

        # Only consider truly empty cells that are not already locked.
        # Use the provided board if available so that user-filled cells are not overwritten.
        empty_cells = [
            (row, col)
            for row in range(9)
            for col in range(9)
            if source_board[row][col] == 0 and (row, col) not in self._locked_cell_positions
        ]

        if not empty_cells:
            raise ValueError("No empty cells available for hints")

        row, col = random.choice(empty_cells)
        value = self._current_puzzle.solution[row][col]
        self._current_puzzle.puzzle[row][col] = value
        self._locked_cells.append({"row": row, "col": col})
        self._locked_cell_positions.add((row, col))
        self.record_hint()

        return {"row": row, "col": col, "value": value}

    def has_active_game(self) -> bool:
        """Check if a game is currently in progress.

        Returns:
            True if a puzzle is loaded, False otherwise.
        """
        return self._current_puzzle is not None

    def reset_game(self) -> None:
        """Clear the current puzzle and reset game state."""
        self._current_puzzle = None
        self._locked_cells = []
        self._locked_cell_positions.clear()
        self._game_start_time = None
        self._current_difficulty = None
        self._hints_used = 0

    def get_locked_cells(self) -> list[dict[str, int]]:
        """Get the list of locked cell positions.

        Returns:
            List of dicts with 'row' and 'col' keys for each locked cell.
        """
        return [cell.copy() for cell in self._locked_cells]

    def is_cell_locked(self, row: int, col: int) -> bool:
        """Check if a cell is locked (prefilled and should not be editable).

        Args:
            row: Row index (0-8)
            col: Column index (0-8)

        Returns:
            True if the cell is locked, False otherwise.
        """
        return (row, col) in self._locked_cell_positions

    @staticmethod
    def _build_locked_cell_cache(board: list[list[int]]) -> tuple[list[dict[str, int]], set[tuple[int, int]]]:
        """Build the locked cell list and lookup set from a puzzle board."""
        locked_cells: list[dict[str, int]] = []
        locked_positions: set[tuple[int, int]] = set()

        for row in range(9):
            for col in range(9):
                if board[row][col] != 0:
                    locked_cells.append({"row": row, "col": col})
                    locked_positions.add((row, col))

        return locked_cells, locked_positions

    def record_hint(self) -> None:
        """Record that a hint was used."""
        self._hints_used += 1

    def get_game_stats(self) -> dict:
        """Get current game statistics.

        Returns:
            Dictionary with game stats: elapsed_time (seconds), difficulty, hints_used
        """
        elapsed_time = 0
        if self._game_start_time is not None:
            elapsed_time = int(time.time() - self._game_start_time)
        
        return {
            "elapsed_time": elapsed_time,
            "difficulty": self._current_difficulty or "Custom",
            "hints_used": self._hints_used
        }
