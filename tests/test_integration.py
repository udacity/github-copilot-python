"""Integration tests for Flask routes and game service together."""

import sys
import os
import pytest

# Add starter directory to path
STARTER_DIR = os.path.join(os.path.dirname(__file__), "..", "starter")
if STARTER_DIR not in sys.path:
    sys.path.insert(0, STARTER_DIR)


class TestFlaskIntegration:
    """Integration tests for Flask routes with game service."""

    def test_full_game_flow(self, client):
        """Test a complete game flow: new game -> check solution."""
        # Start a new game
        response = client.get("/new?clues=35")
        assert response.status_code == 200
        puzzle_data = response.get_json()
        puzzle = puzzle_data["puzzle"]

        # Verify we got a valid puzzle
        assert len(puzzle) == 9
        assert any(cell != 0 for row in puzzle for cell in row)

        # Try to check a solution before the current game would be solved
        incomplete_board = [[0] * 9 for _ in range(9)]
        response = client.post("/check", json={"board": incomplete_board})
        assert response.status_code == 200
        check_data = response.get_json()
        assert "incorrect" in check_data
        assert "complete" in check_data
        assert check_data["complete"] is False

    def test_multiple_games_in_sequence(self, client):
        """Test starting multiple games in sequence."""
        for _ in range(3):
            response = client.get("/new?clues=35")
            assert response.status_code == 200
            assert "puzzle" in response.get_json()

    def test_error_handling_for_invalid_clues(self, client):
        """Test error handling for invalid clue counts."""
        test_cases = [
            ("/new?clues=0", 400),
            ("/new?clues=82", 400),
            ("/new?clues=-1", 400),
            ("/new?clues=abc", 400),
        ]

        for url, expected_status in test_cases:
            response = client.get(url)
            assert response.status_code == expected_status

    def test_check_with_valid_9x9_board(self, client):
        """Test checking a properly formatted 9x9 board."""
        response = client.get("/new?clues=35")
        puzzle_data = response.get_json()
        puzzle = puzzle_data["puzzle"]

        # Create a board that preserves locked cells
        valid_board = [row[:] for row in puzzle]
        # Fill in a few empty cells with valid values
        for i in range(9):
            for j in range(9):
                if valid_board[i][j] == 0:
                    valid_board[i][j] = (i + j) % 9 + 1
                    break
        
        response = client.post("/check", json={"board": valid_board})
        assert response.status_code == 200

    def test_check_with_invalid_board_dimensions(self, client):
        """Test checking with incorrectly sized board."""
        client.get("/new?clues=35")

        invalid_boards = [
            [[0] * 8 for _ in range(9)],  # Wrong column count
            [[0] * 9 for _ in range(8)],  # Wrong row count
            [[0] * 9 for _ in range(10)],  # Too many rows
        ]

        for invalid_board in invalid_boards:
            response = client.post("/check", json={"board": invalid_board})
            assert response.status_code == 400

    def test_check_with_invalid_cell_values(self, client):
        """Test checking with invalid cell values."""
        client.get("/new?clues=35")

        invalid_board = [[0] * 9 for _ in range(9)]
        invalid_board[0][0] = 10  # Invalid: must be 0-9

        response = client.post("/check", json={"board": invalid_board})
        assert response.status_code == 400

    def test_json_response_format(self, client):
        """Test that JSON responses have the correct format."""
        response = client.get("/new?clues=35")
        data = response.get_json()
        assert isinstance(data, dict)
        assert "puzzle" in data
        assert isinstance(data["puzzle"], list)

    def test_check_response_format(self, client):
        """Test that check response has correct format."""
        client.get("/new?clues=35")
        board = [[0] * 9 for _ in range(9)]
        response = client.post("/check", json={"board": board})
        data = response.get_json()
        assert isinstance(data, dict)
        assert "incorrect" in data
        assert "complete" in data
        assert isinstance(data["incorrect"], list)
        assert isinstance(data["complete"], bool)

    def test_different_difficulty_levels(self, client):
        """Test generating puzzles with different difficulty levels."""
        clue_counts = [20, 35, 50, 70]

        for clues in clue_counts:
            response = client.get(f"/new?clues={clues}")
            assert response.status_code == 200
            puzzle = response.get_json()["puzzle"]

            # Count actual clues in puzzle
            actual_clues = sum(1 for row in puzzle for cell in row if cell != 0)
            assert actual_clues == clues
