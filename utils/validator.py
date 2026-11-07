"""Sudoku validation helpers."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

SIZE = 9
EMPTY = 0
BOX_SIZE = 3


class SudokuValidator:
    """Validate Sudoku moves, board completion, and conflict detection."""

    @classmethod
    def is_valid_move(
        cls,
        board: List[List[int]],
        row: int,
        col: int,
        num: int,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check whether placing a number is valid and return error details.

        Args:
            board: A 9x9 Sudoku board.
            row: Target row index (0-8).
            col: Target column index (0-8).
            num: Number to place (1-9).

        Returns:
            A tuple containing:
                - bool: True if the move is valid.
                - dict: Detailed information about validation errors.
        """
        errors: List[str] = []
        row_conflict = False
        col_conflict = False
        box_conflict = False

        if not cls._is_valid_index(row) or not cls._is_valid_index(col):
            errors.append("Row and column must be between 0 and 8.")

        if not cls._is_valid_number(num):
            errors.append("Number must be between 1 and 9.")

        if cls._is_invalid_board(board):
            errors.append("Board must be a 9x9 grid.")

        if errors:
            return False, {
                "valid": False,
                "errors": errors,
                "row_conflict": False,
                "col_conflict": False,
                "box_conflict": False,
            }

        current_value = board[row][col]
        if current_value != EMPTY and current_value != num:
            errors.append("Target cell already contains a different number.")

        if cls._in_row(board, row, col, num):
            row_conflict = True
            errors.append("Duplicate value found in row.")

        if cls._in_column(board, row, col, num):
            col_conflict = True
            errors.append("Duplicate value found in column.")

        if cls._in_box(board, row, col, num):
            box_conflict = True
            errors.append("Duplicate value found in 3x3 box.")

        valid = len(errors) == 0
        return valid, {
            "valid": valid,
            "errors": errors,
            "row_conflict": row_conflict,
            "col_conflict": col_conflict,
            "box_conflict": box_conflict,
            "target_cell": {
                "row": row,
                "col": col,
                "current_value": current_value,
            },
        }

    @classmethod
    def check_completion(cls, board: List[List[int]]) -> Dict[str, Any]:
        """Analyze completion and validation status for a Sudoku board.

        Args:
            board: A Sudoku board.

        Returns:
            A dictionary containing completion status, validity, missing cells,
            and any conflicts detected.
        """
        missing_cells = [
            {"row": r, "col": c}
            for r in range(SIZE)
            for c in range(SIZE)
            if board[r][c] == EMPTY
        ]
        conflicts = cls.find_conflicts(board)
        is_complete = len(missing_cells) == 0
        is_valid_solution = is_complete and len(conflicts) == 0

        return {
            "is_complete": is_complete,
            "is_valid_solution": is_valid_solution,
            "missing_cells": missing_cells,
            "conflicts": conflicts,
        }

    @classmethod
    def find_conflicts(cls, board: List[List[int]]) -> List[Dict[str, Any]]:
        """Return a list of conflicts for duplicate values in the board.

        Args:
            board: A Sudoku board.

        Returns:
            A list of dictionaries describing row, column, and box conflicts.
        """
        conflicts: List[Dict[str, Any]] = []

        if cls._is_invalid_board(board):
            return [{"type": "board", "message": "Board must be a 9x9 grid."}]

        # Row conflicts
        for row in range(SIZE):
            values = {}
            for col in range(SIZE):
                value = board[row][col]
                if value == EMPTY:
                    continue
                values.setdefault(value, []).append((row, col))
            for value, positions in values.items():
                if len(positions) > 1:
                    conflicts.append(
                        {
                            "type": "row",
                            "index": row,
                            "value": value,
                            "positions": [{"row": r, "col": c} for r, c in positions],
                        }
                    )

        # Column conflicts
        for col in range(SIZE):
            values = {}
            for row in range(SIZE):
                value = board[row][col]
                if value == EMPTY:
                    continue
                values.setdefault(value, []).append((row, col))
            for value, positions in values.items():
                if len(positions) > 1:
                    conflicts.append(
                        {
                            "type": "column",
                            "index": col,
                            "value": value,
                            "positions": [{"row": r, "col": c} for r, c in positions],
                        }
                    )

        # Box conflicts
        for box_row in range(0, SIZE, BOX_SIZE):
            for box_col in range(0, SIZE, BOX_SIZE):
                values = {}
                for r in range(box_row, box_row + BOX_SIZE):
                    for c in range(box_col, box_col + BOX_SIZE):
                        value = board[r][c]
                        if value == EMPTY:
                            continue
                        values.setdefault(value, []).append((r, c))
                for value, positions in values.items():
                    if len(positions) > 1:
                        conflicts.append(
                            {
                                "type": "box",
                                "box_row": box_row,
                                "box_col": box_col,
                                "value": value,
                                "positions": [{"row": r, "col": c} for r, c in positions],
                            }
                        )

        return conflicts

    @staticmethod
    def _is_valid_index(index: int) -> bool:
        return 0 <= index < SIZE

    @staticmethod
    def _is_valid_number(num: int) -> bool:
        return 1 <= num <= SIZE

    @staticmethod
    def _is_invalid_board(board: List[List[int]]) -> bool:
        if len(board) != SIZE:
            return True
        return any(len(row) != SIZE for row in board)

    @classmethod
    def _in_row(cls, board: List[List[int]], row: int, col: int, num: int) -> bool:
        return any(board[row][c] == num for c in range(SIZE) if c != col)

    @classmethod
    def _in_column(cls, board: List[List[int]], row: int, col: int, num: int) -> bool:
        return any(board[r][col] == num for r in range(SIZE) if r != row)

    @classmethod
    def _in_box(cls, board: List[List[int]], row: int, col: int, num: int) -> bool:
        box_row_start = (row // BOX_SIZE) * BOX_SIZE
        box_col_start = (col // BOX_SIZE) * BOX_SIZE
        for r in range(box_row_start, box_row_start + BOX_SIZE):
            for c in range(box_col_start, box_col_start + BOX_SIZE):
                if (r, c) != (row, col) and board[r][c] == num:
                    return True
        return False
