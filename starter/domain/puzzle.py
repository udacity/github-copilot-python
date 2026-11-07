"""Puzzle generation and management.

This module handles the creation and manipulation of Sudoku puzzles,
including board generation and solution tracking.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from domain.board import SudokuBoard, SIZE, EMPTY
from utils.generation import SudokuGenerator


@dataclass
class Puzzle:
    """Represents a Sudoku puzzle with its solution.

    Attributes:
        puzzle: The puzzle grid (with clues visible)
        solution: The complete solution grid
        clues: Number of clues (filled cells) in the puzzle
    """

    puzzle: List[List[int]]
    solution: List[List[int]]
    clues: int

    def validate(self) -> bool:
        """Validate that the puzzle and solution are consistent.

        Returns:
            True if puzzle is valid, False otherwise.
        """
        if len(self.puzzle) != SIZE or len(self.solution) != SIZE:
            return False

        for row in range(SIZE):
            for col in range(SIZE):
                puzzle_cell = self.puzzle[row][col]
                solution_cell = self.solution[row][col]
                if puzzle_cell != EMPTY and puzzle_cell != solution_cell:
                    return False

        return SudokuBoard.is_valid_solution(self.solution)


class PuzzleGenerator:
    """Generates valid Sudoku puzzles with unique solutions."""

    @staticmethod
    def generate(clues: int = 35) -> Puzzle:
        """Generate a Sudoku puzzle with the specified number of clues.

        Args:
            clues: Number of clues (1-81). Default is 35.

        Returns:
            A Puzzle object containing the puzzle and solution.

        Raises:
            ValueError: If clues is not between 1 and 81.
        """
        if not (1 <= clues <= SIZE * SIZE):
            raise ValueError(f"Clues must be between 1 and {SIZE * SIZE}")

        puzzle, solution = SudokuGenerator.generate_puzzle(clues=clues)
        return Puzzle(puzzle=puzzle, solution=solution, clues=clues)
