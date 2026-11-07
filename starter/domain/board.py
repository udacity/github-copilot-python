"""Sudoku board operations and constraint validation.

This module provides utilities for working with Sudoku boards,
including validation, constraint checking, and board manipulation.
"""

from typing import List


# Constants
SIZE: int = 9
EMPTY: int = 0
BOX_SIZE: int = 3


class SudokuBoard:
    """Represents a Sudoku board with operations and constraints."""

    def __init__(self) -> None:
        """Initialize an empty Sudoku board."""
        self.grid: List[List[int]] = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

    @staticmethod
    def create_empty() -> List[List[int]]:
        """Create an empty 9x9 Sudoku board.

        Returns:
            A 9x9 grid of zeros representing empty cells.
        """
        return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

    @staticmethod
    def is_safe(board: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if placing a number at (row, col) is valid.

        Validates that the number does not violate Sudoku rules:
        - No duplicate in the same row
        - No duplicate in the same column
        - No duplicate in the same 3x3 box

        Args:
            board: The Sudoku board grid
            row: Row index (0-8)
            col: Column index (0-8)
            num: Number to place (1-9)

        Returns:
            True if placement is valid, False otherwise.
        """
        # Check row
        if num in board[row]:
            return False

        # Check column
        if num in [board[i][col] for i in range(SIZE)]:
            return False

        # Check 3x3 box
        box_row_start = row - row % BOX_SIZE
        box_col_start = col - col % BOX_SIZE
        for i in range(BOX_SIZE):
            for j in range(BOX_SIZE):
                if board[box_row_start + i][box_col_start + j] == num:
                    return False

        return True

    @staticmethod
    def deep_copy(board: List[List[int]]) -> List[List[int]]:
        """Create a deep copy of a board.

        Args:
            board: The board to copy

        Returns:
            A new independent copy of the board.
        """
        return [row[:] for row in board]

    @staticmethod
    def is_complete(board: List[List[int]]) -> bool:
        """Check if the board is completely filled.

        Args:
            board: The Sudoku board

        Returns:
            True if all cells are filled (no zeros), False otherwise.
        """
        return all(cell != EMPTY for row in board for cell in row)

    @staticmethod
    def is_valid_solution(board: List[List[int]]) -> bool:
        """Verify that a completed board is a valid solution.

        Args:
            board: The completed Sudoku board

        Returns:
            True if the solution is valid, False otherwise.
        """
        if not SudokuBoard.is_complete(board):
            return False

        # Check all rows contain 1-9
        for row in board:
            if sorted(row) != list(range(1, SIZE + 1)):
                return False

        # Check all columns contain 1-9
        for col in range(SIZE):
            column = [board[row][col] for row in range(SIZE)]
            if sorted(column) != list(range(1, SIZE + 1)):
                return False

        # Check all 3x3 boxes contain 1-9
        for box_row in range(0, SIZE, BOX_SIZE):
            for box_col in range(0, SIZE, BOX_SIZE):
                box = [
                    board[r][c]
                    for r in range(box_row, box_row + BOX_SIZE)
                    for c in range(box_col, box_col + BOX_SIZE)
                ]
                if sorted(box) != list(range(1, SIZE + 1)):
                    return False

        return True
