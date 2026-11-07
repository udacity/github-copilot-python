"""Sudoku puzzle generator utility."""

from __future__ import annotations

import random
from typing import List, Tuple

from config import DIFFICULTY_RANGES


class SudokuGenerator:
    """Generate Sudoku puzzles and verify uniqueness of solutions."""

    SIZE = 9
    BOX_SIZE = 3
    EMPTY = 0

    @classmethod
    def generate_puzzle(
        cls,
        difficulty: str = "medium",
        clues: int | None = None,
    ) -> Tuple[List[List[int]], List[List[int]]]:
        """Generate a Sudoku puzzle and its full solution.

        Args:
            difficulty: Difficulty level, one of 'easy', 'medium', or 'hard'.
            clues: Exact number of prefilled cells, if specified.

        Returns:
            A tuple containing the generated puzzle board and the full solution board.

        Raises:
            ValueError: If the requested difficulty or clues are invalid.
        """
        if clues is not None:
            if not isinstance(clues, int) or not (1 <= clues <= 81):
                raise ValueError("Clues must be an integer between 1 and 81.")
        else:
            if difficulty not in DIFFICULTY_RANGES:
                raise ValueError(
                    f"Invalid difficulty '{difficulty}'. Choose easy, medium, or hard."
                )
            min_clues, max_clues = DIFFICULTY_RANGES[difficulty]
            clues = random.randint(min_clues, max_clues)

        board = cls._create_empty_board()
        cls._fill_board(board)
        solution = cls._deep_copy(board)
        puzzle = cls._remove_cells_to_clues(board, clues)

        return puzzle, solution

    @classmethod
    def ensure_unique_solution(cls, board: List[List[int]]) -> bool:
        """Check whether a Sudoku board has a unique valid solution.

        Args:
            board: A partially filled Sudoku board.

        Returns:
            True if there is exactly one valid solution, False otherwise.
        """
        board_copy = cls._deep_copy(board)
        return cls._count_solutions(board_copy, limit=2) == 1

    @classmethod
    def _create_empty_board(cls) -> List[List[int]]:
        return [[cls.EMPTY for _ in range(cls.SIZE)] for _ in range(cls.SIZE)]

    @classmethod
    def _deep_copy(cls, board: List[List[int]]) -> List[List[int]]:
        return [row.copy() for row in board]

    @classmethod
    def _fill_board(cls, board: List[List[int]]) -> bool:
        empty = cls._find_empty(board)
        if empty is None:
            return True

        row, col = empty
        numbers = list(range(1, cls.SIZE + 1))
        random.shuffle(numbers)

        for value in numbers:
            if cls._is_safe(board, row, col, value):
                board[row][col] = value
                if cls._fill_board(board):
                    return True
                board[row][col] = cls.EMPTY

        return False

    @classmethod
    def _remove_cells_to_clues(cls, board: List[List[int]], clues: int) -> List[List[int]]:
        puzzle = cls._deep_copy(board)
        filled_positions = [(r, c) for r in range(cls.SIZE) for c in range(cls.SIZE)]
        random.shuffle(filled_positions)

        while sum(1 for r in range(cls.SIZE) for c in range(cls.SIZE) if puzzle[r][c] != cls.EMPTY) > clues:
            if not filled_positions:
                break

            row, col = filled_positions.pop()
            removed_value = puzzle[row][col]
            puzzle[row][col] = cls.EMPTY

            if not cls.ensure_unique_solution(puzzle):
                puzzle[row][col] = removed_value

        return puzzle

    @classmethod
    def _count_solutions(cls, board: List[List[int]], limit: int = 2) -> int:
        empty = cls._find_empty(board)
        if empty is None:
            return 1

        row, col = empty
        count = 0

        for value in range(1, cls.SIZE + 1):
            if cls._is_safe(board, row, col, value):
                board[row][col] = value
                count += cls._count_solutions(board, limit)
                board[row][col] = cls.EMPTY
                if count >= limit:
                    return count

        return count

    @classmethod
    def _find_empty(cls, board: List[List[int]]) -> Tuple[int, int] | None:
        for row in range(cls.SIZE):
            for col in range(cls.SIZE):
                if board[row][col] == cls.EMPTY:
                    return row, col
        return None

    @classmethod
    def _is_safe(cls, board: List[List[int]], row: int, col: int, value: int) -> bool:
        if any(board[row][c] == value for c in range(cls.SIZE)):
            return False

        if any(board[r][col] == value for r in range(cls.SIZE)):
            return False

        box_row = (row // cls.BOX_SIZE) * cls.BOX_SIZE
        box_col = (col // cls.BOX_SIZE) * cls.BOX_SIZE
        for r in range(box_row, box_row + cls.BOX_SIZE):
            for c in range(box_col, box_col + cls.BOX_SIZE):
                if board[r][c] == value:
                    return False

        return True
