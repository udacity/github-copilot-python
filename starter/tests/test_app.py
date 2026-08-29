import pytest

import app
import game


@pytest.fixture(autouse=True)
def reset_current_game():
    app.CURRENT['puzzle'] = None
    app.CURRENT['solution'] = None
    app.CURRENT['hints_used'] = 0
    yield
    app.CURRENT['puzzle'] = None
    app.CURRENT['solution'] = None


@pytest.fixture
def client():
    app.app.config.update(TESTING=True)
    with app.app.test_client() as test_client:
        yield test_client


def test_index_renders_sudoku_game_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data


def test_new_game_returns_puzzle_and_stores_game_state(client, monkeypatch):
    puzzle = [[0 for _ in range(app.sudoku_logic.SIZE)] for _ in range(app.sudoku_logic.SIZE)]
    solution = [[1 for _ in range(app.sudoku_logic.SIZE)] for _ in range(app.sudoku_logic.SIZE)]

    def fake_generate_puzzle(clues):
        assert clues == 35
        return puzzle, solution

    monkeypatch.setattr(app.sudoku_logic, 'generate_puzzle', fake_generate_puzzle)

    response = client.get('/new')

    assert response.status_code == 200
    assert response.get_json() == {'puzzle': puzzle}
    assert app.CURRENT == {
        'puzzle': puzzle,
        'solution': solution,
        'hints_used': 0,
    }


@pytest.mark.parametrize('difficulty, clues', [
    ('easy', 45),
    ('medium', 35),
    ('hard', 25),
])
def test_new_game_uses_difficulty_clue_target(client, monkeypatch, difficulty, clues):
    puzzle = [[0 for _ in range(app.sudoku_logic.SIZE)] for _ in range(app.sudoku_logic.SIZE)]
    solution = [[1 for _ in range(app.sudoku_logic.SIZE)] for _ in range(app.sudoku_logic.SIZE)]

    def fake_generate_puzzle(received_clues):
        assert received_clues == clues
        return puzzle, solution

    monkeypatch.setattr(app.sudoku_logic, 'generate_puzzle', fake_generate_puzzle)

    response = client.get(f'/new?difficulty={difficulty}')

    assert response.status_code == 200
    assert response.get_json() == {'puzzle': puzzle}


def test_new_game_rejects_unknown_difficulty(client):
    response = client.get('/new?difficulty=expert')

    assert response.status_code == 400


def test_check_solution_requires_an_active_game(client):
    response = client.post('/check', json={'board': []})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_solution_reports_incorrect_cells(client):
    solution = [[1 for _ in range(app.sudoku_logic.SIZE)] for _ in range(app.sudoku_logic.SIZE)]
    app.CURRENT['solution'] = solution
    board = [row[:] for row in solution]
    board[2][4] = 0

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [[2, 4]]}


def test_check_solution_returns_no_incorrect_cells_for_matching_board(client):
    solution = [[1 for _ in range(app.sudoku_logic.SIZE)] for _ in range(app.sudoku_logic.SIZE)]
    app.CURRENT['solution'] = solution

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_completed_game_returns_stable_elapsed_time(client, monkeypatch):
    puzzle = [[0 for _ in range(app.sudoku_logic.SIZE)] for _ in range(app.sudoku_logic.SIZE)]
    solution = [[1 for _ in range(app.sudoku_logic.SIZE)] for _ in range(app.sudoku_logic.SIZE)]

    monkeypatch.setattr(app.sudoku_logic, 'generate_puzzle', lambda clues: (puzzle, solution))
    clock = iter([100.0, 112.5])
    monkeypatch.setattr(game.time, 'monotonic', lambda: next(clock))

    client.get('/new')
    board = [row[:] for row in solution]

    response = client.post('/check', json={'board': board})
    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [], 'elapsed_seconds': 12}

    response = client.post('/check', json={'board': board})
    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [], 'elapsed_seconds': 12}


def test_hint_fills_an_empty_cell_and_increments_hint_count(client):
    app.CURRENT['puzzle'] = [[0, 0] + [3] * 7] + [[4] * 9 for _ in range(8)]
    app.CURRENT['solution'] = [[1, 2] + [3] * 7] + [[4] * 9 for _ in range(8)]
    board = [row[:] for row in app.CURRENT['puzzle']]
    board[0][0] = 8

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {
        'row': 0,
        'col': 1,
        'value': 2,
        'hints_used': 1,
    }
    assert board[0][0] == 8


def test_hint_does_not_overwrite_user_entered_empty_puzzle_cells(client):
    app.CURRENT['puzzle'] = [[0] + [2] * 8] + [[3] * 9 for _ in range(8)]
    app.CURRENT['solution'] = [[1] + [2] * 8] + [[3] * 9 for _ in range(8)]
    board = [row[:] for row in app.CURRENT['puzzle']]
    board[0][0] = 9

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No empty cells remain'}
    assert app.CURRENT['hints_used'] == 0


def test_hint_requires_an_active_game(client):
    response = client.post('/hint', json={'board': []})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}