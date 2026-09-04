import app as app_module
import sudoku_logic
import pytest


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    app_module.CURRENT["puzzle"] = None
    app_module.CURRENT["solution"] = None

    with app_module.app.test_client() as test_client:
        yield test_client

    app_module.CURRENT["puzzle"] = None
    app_module.CURRENT["solution"] = None


def test_index_returns_game_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Sudoku Game" in response.data


def test_new_game_returns_puzzle(client):
    response = client.get("/new?clues=35")

    assert response.status_code == 200
    data = response.get_json()

    assert "puzzle" in data
    assert len(data["puzzle"]) == 9
    assert all(len(row) == 9 for row in data["puzzle"])


def test_check_requires_game_in_progress(client):
    response = client.post("/check", json={"board": []})

    assert response.status_code == 400
    assert response.get_json() == {"error": "No game in progress"}


def test_check_accepts_current_solution(client):
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)
    app_module.CURRENT["puzzle"] = puzzle
    app_module.CURRENT["solution"] = solution

    response = client.post("/check", json={"board": solution})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": []}


def test_check_reports_incorrect_cells(client):
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)
    app_module.CURRENT["puzzle"] = puzzle
    app_module.CURRENT["solution"] = solution

    board = [row[:] for row in solution]
    board[0][0] = 0

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json()["incorrect"] == [[0, 0]]

@pytest.mark.parametrize(
    ("difficulty", "expected_clues"),
    [
        ("easy", 45),
        ("medium", 35),
        ("hard", 25),
    ],
)
def test_new_game_uses_selected_difficulty(
    client,
    difficulty,
    expected_clues,
):
    response = client.get(f"/new?difficulty={difficulty}")

    assert response.status_code == 200

    puzzle = response.get_json()["puzzle"]
    clues = sum(
        cell != sudoku_logic.EMPTY
        for row in puzzle
        for cell in row
    )

    assert clues == expected_clues


def test_new_game_rejects_invalid_difficulty(client):
    response = client.get("/new?difficulty=expert")

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "difficulty must be easy, medium, or hard"
    }