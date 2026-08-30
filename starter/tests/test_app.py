import sys
import os

# Ensure the starter package directory is importable (tests located in starter/tests)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app


def test_index_route_renders_page():
    client = flask_app.test_client()
    res = client.get('/')
    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert 'Sudoku Game' in text
    assert 'difficulty' in text.lower()
    assert 'Hint' in text
    assert 'Check' in text
    assert 'Top 10 Fastest Times' in text




def test_index_page_has_game_controls():
    client = flask_app.test_client()
    res = client.get('/')
    assert res.status_code == 200
    text = res.get_data(as_text=True)
    for token in ['difficulty', 'new-game', 'hint-button', 'check-button', 'theme-toggle', 'scoreboard', 'timer']:
        assert token in text

def test_new_game_route_supports_difficulty_selection():
    client = flask_app.test_client()
    res = client.get('/new?difficulty=easy')
    assert res.status_code == 200
    payload = res.get_json()
    assert payload['difficulty'] == 'easy'
    assert payload['solution']
    assert len(payload['puzzle']) == 9
    assert len(payload['solution']) == 9
    assert sum(1 for row in payload['puzzle'] for cell in row if cell != 0) == 45
