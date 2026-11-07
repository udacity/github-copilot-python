"""Unit tests for the domain layer (board, puzzle generation, validation)."""

import sys
import os

# Add starter directory to path
STARTER_DIR = os.path.join(os.path.dirname(__file__), "..", "starter")
if STARTER_DIR not in sys.path:
    sys.path.insert(0, STARTER_DIR)

from domain.board import SudokuBoard, SIZE, EMPTY
from domain.puzzle import Puzzle, PuzzleGenerator
from domain.game import GameService


class TestSudokuBoard:
    """Tests for SudokuBoard operations."""

    def test_create_empty_board(self):
        """Test creating an empty board."""
        board = SudokuBoard.create_empty()
        assert len(board) == SIZE
        assert all(len(row) == SIZE for row in board)
        assert all(cell == EMPTY for row in board for cell in row)

    def test_is_safe_valid_placement(self):
        """Test is_safe returns True for valid placements."""
        board = SudokuBoard.create_empty()
        assert SudokuBoard.is_safe(board, 0, 0, 1)

    def test_is_safe_duplicate_in_row(self):
        """Test is_safe returns False for duplicate in row."""
        board = SudokuBoard.create_empty()
        board[0][0] = 1
        assert not SudokuBoard.is_safe(board, 0, 1, 1)

    def test_is_safe_duplicate_in_column(self):
        """Test is_safe returns False for duplicate in column."""
        board = SudokuBoard.create_empty()
        board[0][0] = 1
        assert not SudokuBoard.is_safe(board, 1, 0, 1)

    def test_is_safe_duplicate_in_box(self):
        """Test is_safe returns False for duplicate in 3x3 box."""
        board = SudokuBoard.create_empty()
        board[0][0] = 1
        assert not SudokuBoard.is_safe(board, 1, 1, 1)

    def test_deep_copy(self):
        """Test deep_copy creates an independent copy."""
        board = SudokuBoard.create_empty()
        board[0][0] = 5
        copied = SudokuBoard.deep_copy(board)
        copied[0][0] = 9
        assert board[0][0] == 5

    def test_is_complete_empty_board(self):
        """Test is_complete returns False for empty board."""
        board = SudokuBoard.create_empty()
        assert not SudokuBoard.is_complete(board)

    def test_is_complete_full_board(self):
        """Test is_complete returns True for full board."""
        board = [[i + 1 for i in range(SIZE)] for _ in range(SIZE)]
        assert SudokuBoard.is_complete(board)

    def test_is_valid_solution_valid(self):
        """Test is_valid_solution recognizes valid solution."""
        # Create a valid solution
        puzzle = PuzzleGenerator.generate(clues=35)
        assert SudokuBoard.is_valid_solution(puzzle.solution)

    def test_is_valid_solution_incomplete(self):
        """Test is_valid_solution rejects incomplete board."""
        board = SudokuBoard.create_empty()
        assert not SudokuBoard.is_valid_solution(board)


class TestPuzzleGenerator:
    """Tests for puzzle generation."""

    def test_generate_puzzle_returns_valid_9x9_grid(self):
        """Test that generated puzzle is 9x9."""
        puzzle = PuzzleGenerator.generate(clues=35)
        assert len(puzzle.puzzle) == 9
        assert len(puzzle.solution) == 9
        assert all(len(row) == 9 for row in puzzle.puzzle)
        assert all(len(row) == 9 for row in puzzle.solution)

    def test_generate_puzzle_solution_is_complete_and_valid(self):
        """Test that solution is complete and valid."""
        puzzle = PuzzleGenerator.generate(clues=40)

        # Solution should be complete (no zeros)
        assert all(cell != EMPTY for row in puzzle.solution for cell in row)

        # Solution should be valid
        assert SudokuBoard.is_valid_solution(puzzle.solution)

    def test_generate_puzzle_clue_count(self):
        """Test that puzzle has approximately correct number of clues."""
        for clues in [20, 35, 50]:
            puzzle = PuzzleGenerator.generate(clues=clues)
            puzzle_clue_count = sum(1 for row in puzzle.puzzle for cell in row if cell != EMPTY)
            assert puzzle_clue_count == clues

    def test_generate_puzzle_puzzle_matches_solution(self):
        """Test that all clues in puzzle match solution."""
        puzzle = PuzzleGenerator.generate(clues=35)
        for i in range(SIZE):
            for j in range(SIZE):
                if puzzle.puzzle[i][j] != EMPTY:
                    assert puzzle.puzzle[i][j] == puzzle.solution[i][j]

    def test_generate_puzzle_invalid_clues_count(self):
        """Test that invalid clue counts raise ValueError."""
        with pytest.raises(ValueError):
            PuzzleGenerator.generate(clues=0)

        with pytest.raises(ValueError):
            PuzzleGenerator.generate(clues=82)

    def test_puzzle_validate(self):
        """Test Puzzle validation."""
        puzzle = PuzzleGenerator.generate(clues=35)
        assert puzzle.validate()


class TestGameService:
    """Tests for the GameService."""

    def test_new_game(self, game_service):
        """Test starting a new game."""
        puzzle = game_service.new_game(difficulty="medium")
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)
        assert game_service.has_active_game()

    def test_check_solution_no_game(self, game_service):
        """Test checking solution when no game is in progress."""
        board = [[0] * 9 for _ in range(9)]
        with pytest.raises(RuntimeError):
            game_service.check_solution(board)

    def test_check_solution_with_correct_answer(self, game_service):
        """Test checking a correct solution."""
        game_service.new_game(difficulty="medium")
        puzzle = game_service.get_current_puzzle()
        incorrect, is_complete = game_service.check_solution(puzzle.solution)
        assert len(incorrect) == 0
        assert is_complete

    def test_check_solution_with_incorrect_answer(self, game_service):
        """Test checking an incorrect solution."""
        game_service.new_game(difficulty="medium")
        puzzle = game_service.get_current_puzzle()

        # Create an incorrect board (modify an empty cell in the puzzle)
        incorrect_board = [row[:] for row in puzzle.solution]
        
        # Find an empty cell (where puzzle has 0) to modify
        modified = False
        for i in range(9):
            for j in range(9):
                if puzzle.puzzle[i][j] == 0:  # Empty cell
                    # Change it to wrong value
                    incorrect_board[i][j] = (incorrect_board[i][j] % 9) + 1
                    modified = True
                    break
            if modified:
                break

        incorrect, is_complete = game_service.check_solution(incorrect_board)
        assert len(incorrect) > 0
        assert not is_complete

    def test_reset_game(self, game_service):
        """Test resetting the game."""
        game_service.new_game(difficulty="medium")
        assert game_service.has_active_game()

        game_service.reset_game()
        assert not game_service.has_active_game()
        assert game_service.get_current_puzzle() is None


import pytest

