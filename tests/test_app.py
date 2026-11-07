"""Integration tests for Flask routes."""

import pytest


def test_index_route(client):
    """Test that the index route returns HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"<html" in response.data.lower() or b"<!doctype html>" in response.data.lower()


def test_new_game_route_returns_puzzle(client):
    """Test that /new returns a valid puzzle grid."""
    response = client.get("/new?clues=35")
    assert response.status_code == 200

    body = response.get_json()
    assert isinstance(body, dict)
    assert "puzzle" in body

    puzzle = body["puzzle"]
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)


def test_new_game_route_default_clues(client):
    """Test that /new uses default clues when not specified."""
    response = client.get("/new")
    assert response.status_code == 200
    body = response.get_json()
    assert "puzzle" in body


def test_new_game_route_invalid_clues(client):
    """Test that /new returns 400 for invalid clues."""
    response = client.get("/new?clues=100")
    assert response.status_code == 400
    body = response.get_json()
    assert "error" in body


def test_check_solution_no_game(client):
    """Test that /check returns 400 when no game is in progress."""
    response = client.post("/check", json={"board": [[0] * 9 for _ in range(9)]})
    assert response.status_code == 400
    body = response.get_json()
    assert "error" in body
    assert body["error"] == "No game in progress"


def test_check_solution_with_game(client):
    """Test that /check works when a game is in progress."""
    # Start a new game
    new_game_response = client.get("/new?clues=35")
    assert new_game_response.status_code == 200

    # Check a solution (we'll just use a board of zeros to test the flow)
    response = client.post("/check", json={"board": [[0] * 9 for _ in range(9)]})
    assert response.status_code == 200

    body = response.get_json()
    assert "incorrect" in body
    assert "complete" in body


def test_check_solution_missing_board(client):
    """Test that /check returns 400 when board is missing."""
    client.get("/new?clues=35")  # Start a game
    response = client.post("/check", json={})
    assert response.status_code == 400
    body = response.get_json()
    assert "error" in body


def test_check_solution_invalid_board_format(client):
    """Test that /check returns 400 for invalid board format."""
    client.get("/new?clues=35")  # Start a game
    response = client.post("/check", json={"board": [[0] * 8 for _ in range(9)]})
    assert response.status_code == 400
    body = response.get_json()
    assert "error" in body


def test_validate_endpoint_returns_conflicts(client):
    """Test that /validate returns conflicts for an invalid board."""
    invalid_board = [[0] * 9 for _ in range(9)]
    invalid_board[0][0] = 1
    invalid_board[0][1] = 1

    response = client.post("/validate", json={"board": invalid_board})
    assert response.status_code == 200

    body = response.get_json()
    assert "conflicts" in body
    conflicts = body["conflicts"]
    assert isinstance(conflicts, list)
    assert any(conflict["type"] == "row" and conflict["index"] == 0 for conflict in conflicts)


def test_validate_endpoint_missing_board(client):
    """Test that /validate returns 400 when board is missing."""
    response = client.post("/validate", json={})
    assert response.status_code == 400
    body = response.get_json()
    assert "error" in body


def test_validate_endpoint_invalid_board_format(client):
    """Test that /validate returns 400 for invalid board format."""
    response = client.post("/validate", json={"board": [[0] * 8 for _ in range(9)]})
    assert response.status_code == 400
    body = response.get_json()
    assert "error" in body


def test_check_complete_endpoint_returns_complete_status(client):
    """Test that /check-complete returns completion status for a valid board."""
    # Create a valid complete Sudoku board
    complete_board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ]
    
    response = client.post("/check-complete", json={"board": complete_board})
    assert response.status_code == 200

    body = response.get_json()
    assert "is_complete" in body
    assert "message" in body
    assert "elapsed_time" in body
    assert "difficulty" in body
    assert "hints_used" in body
    assert body["is_complete"] is True
    assert "Congratulations" in body["message"]
    assert body["elapsed_time"] >= 0
    assert body["hints_used"] == 0


def test_check_complete_endpoint_returns_incomplete_status(client):
    """Test that /check-complete returns incomplete status for an incomplete board."""
    incomplete_board = [[0] * 9 for _ in range(9)]
    incomplete_board[0][0] = 1  # Add one number
    
    response = client.post("/check-complete", json={"board": incomplete_board})
    assert response.status_code == 200

    body = response.get_json()
    assert "is_complete" in body
    assert "message" in body
    assert body["is_complete"] is False
    assert "not yet complete" in body["message"]


def test_check_complete_endpoint_missing_board(client):
    """Test that /check-complete returns 400 when board is missing."""
    response = client.post("/check-complete", json={})
    assert response.status_code == 400
    body = response.get_json()
    assert "error" in body


def test_hint_endpoint_returns_a_hint(client):
    """Test that /hint returns a random empty cell and value."""
    response = client.get("/new?clues=35")
    assert response.status_code == 200

    hint_response = client.post("/hint")
    assert hint_response.status_code == 200

    hint_data = hint_response.get_json()
    assert "row" in hint_data
    assert "col" in hint_data
    assert "value" in hint_data
    assert 0 <= hint_data["row"] < 9
    assert 0 <= hint_data["col"] < 9
    assert 1 <= hint_data["value"] <= 9


def test_hint_endpoint_skips_filled_board_cell(client):
    """Test that /hint skips an already populated unlocked cell in the submitted board."""
    response = client.get("/new?clues=35")
    assert response.status_code == 200

    body = response.get_json()
    puzzle = body["puzzle"]
    locked_cells = body["locked_cells"]

    board = [row[:] for row in puzzle]
    target_row = None
    target_col = None
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0 and not any(cell["row"] == i and cell["col"] == j for cell in locked_cells):
                target_row = i
                target_col = j
                break
        if target_row is not None:
            break

    assert target_row is not None and target_col is not None
    board[target_row][target_col] = 1

    hint_response = client.post("/hint", json={"board": board})
    assert hint_response.status_code == 200

    hint_data = hint_response.get_json()
    assert (hint_data["row"], hint_data["col"]) != (target_row, target_col)
    assert "row" in hint_data
    assert "col" in hint_data
    assert "value" in hint_data


def test_check_complete_endpoint_invalid_board_format(client):
    """Test that /check-complete returns 400 for invalid board format."""
    response = client.post("/check-complete", json={"board": [[0] * 8 for _ in range(9)]})
    assert response.status_code == 400
    body = response.get_json()
    assert "error" in body


def test_get_scores_endpoint(client):
    """Test that /scores GET returns top scores."""
    response = client.get("/scores")
    assert response.status_code == 200

    body = response.get_json()
    assert "scores" in body
    assert isinstance(body["scores"], list)


def test_save_score_endpoint(client):
    """Test that /scores POST saves a new score."""
    score = {
        "name": "TestPlayer",
        "elapsed_time": 120,
        "difficulty": "medium",
        "hints_used": 2,
    }

    response = client.post("/scores", json=score)
    assert response.status_code == 200

    body = response.get_json()
    assert "success" in body
    assert body["success"] is True

    get_response = client.get("/scores")
    assert get_response.status_code == 200
    scores = get_response.get_json()["scores"]
    assert any(s["name"] == "TestPlayer" and s["elapsed_time"] == 120 for s in scores)


def test_save_score_invalid_name(client):
    """Test that /scores POST rejects invalid name."""
    score = {
        "name": "",
        "elapsed_time": 120,
        "difficulty": "medium",
        "hints_used": 2,
    }

    response = client.post("/scores", json=score)
    assert response.status_code == 400
    body = response.get_json()
    assert "error" in body


def test_save_score_invalid_time(client):
    """Test that /scores POST rejects invalid time."""
    score = {
        "name": "TestPlayer",
        "elapsed_time": "invalid",
        "difficulty": "medium",
        "hints_used": 2,
    }

    response = client.post("/scores", json=score)
    assert response.status_code == 400
    body = response.get_json()
    assert "error" in body

