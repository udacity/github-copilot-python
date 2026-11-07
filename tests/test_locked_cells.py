import os
import sys

# Add starter directory to path
STARTER_DIR = os.path.join(os.path.dirname(__file__), "..", "starter")
if STARTER_DIR not in sys.path:
    sys.path.insert(0, STARTER_DIR)

import pytest
from domain.game import GameService


class TestLockedCells:
    """Tests for locked cells functionality."""

    def test_new_game_marks_prefilled_cells_as_locked(self, game_service):
        """Test that prefilled cells are marked as locked after new game."""
        puzzle = game_service.new_game(difficulty="medium")
        locked_cells = game_service.get_locked_cells()

        assert len(locked_cells) > 0
        assert all("row" in cell and "col" in cell for cell in locked_cells)

        # Verify locked cells match puzzle clues
        for cell in locked_cells:
            assert puzzle[cell["row"]][cell["col"]] != 0

    def test_is_cell_locked(self, game_service):
        """Test checking if a cell is locked."""
        game_service.new_game(clues=35)
        locked_cells = game_service.get_locked_cells()

        assert len(locked_cells) > 0
        
        for cell in locked_cells:
            assert game_service.is_cell_locked(cell["row"], cell["col"]) is True

        # Find an empty cell and verify it's not locked
        empty_found = False
        for i in range(9):
            for j in range(9):
                if not game_service.is_cell_locked(i, j):
                    empty_found = True
                    break
        assert empty_found

    def test_check_solution_rejects_modified_locked_cells(self, game_service):
        """Test that modifying locked cells raises ValueError."""
        puzzle = game_service.new_game(clues=35)
        solution = game_service.get_current_puzzle().solution

        # Create a board with a modified locked cell
        modified_board = [row[:] for row in solution]
        locked_cells = game_service.get_locked_cells()
        
        if locked_cells:
            locked = locked_cells[0]
            original_value = puzzle[locked["row"]][locked["col"]]
            
            # Only test if this cell is actually prefilled (not 0)
            if original_value != 0:
                # Change it to a different value
                modified_board[locked["row"]][locked["col"]] = (original_value % 9) + 1

                with pytest.raises(ValueError):
                    game_service.check_solution(modified_board)

    def test_reset_game_clears_locked_cells(self, game_service):
        """Test that resetting the game clears locked cells."""
        game_service.new_game(clues=35)
        assert len(game_service.get_locked_cells()) > 0

        game_service.reset_game()
        assert len(game_service.get_locked_cells()) == 0

    def test_hint_adds_locked_cell_and_increments_hints(self, game_service):
        """Test that a hint fills an empty cell and increments hints used."""
        puzzle = game_service.new_game(clues=35)
        empty_positions = [
            (i, j)
            for i in range(9)
            for j in range(9)
            if puzzle[i][j] == 0
        ]
        assert empty_positions

        initial_locked = len(game_service.get_locked_cells())
        hint = game_service.hint()

        assert isinstance(hint, dict)
        assert "row" in hint and "col" in hint and "value" in hint
        assert 0 <= hint["row"] < 9
        assert 0 <= hint["col"] < 9
        assert 1 <= hint["value"] <= 9

        assert (hint["row"], hint["col"]) in empty_positions
        assert puzzle[hint["row"]][hint["col"]] == hint["value"]
        assert len(game_service.get_locked_cells()) == initial_locked + 1
        assert game_service.is_cell_locked(hint["row"], hint["col"])
        assert game_service.get_game_stats()["hints_used"] == 1

    def test_hint_skips_user_filled_cells(self, game_service):
        """Test that hint selection ignores user-filled unlocked cells."""
        puzzle = game_service.new_game(clues=35)
        current_puzzle = game_service.get_current_puzzle()
        assert current_puzzle is not None

        solution = current_puzzle.solution
        filled_board = [row[:] for row in puzzle]

        # Find an empty unlocked cell and prefill it in the board payload.
        target_row = None
        target_col = None
        for i in range(9):
            for j in range(9):
                if filled_board[i][j] == 0 and not game_service.is_cell_locked(i, j):
                    target_row = i
                    target_col = j
                    break
            if target_row is not None:
                break

        assert target_row is not None and target_col is not None
        filled_board[target_row][target_col] = solution[target_row][target_col]

        hint = game_service.hint(filled_board)

        assert isinstance(hint, dict)
        assert (hint["row"], hint["col"]) != (target_row, target_col)
        assert filled_board[hint["row"]][hint["col"]] == 0
        assert hint["value"] == solution[hint["row"]][hint["col"]]
