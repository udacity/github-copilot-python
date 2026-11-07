from datetime import datetime

from models.game_state import GameState


def test_game_state_defaults_and_fields():
    state = GameState()

    assert len(state.board) == 9
    assert all(len(row) == 9 for row in state.board)
    assert state.difficulty == "medium"
    assert state.start_time is None
    assert state.hints_used == 0
    assert state.locked_cells == []
    assert state.is_complete is False


def test_game_state_to_dict_and_from_dict():
    now = datetime.utcnow().replace(microsecond=0)
    state = GameState(
        board=[[1 if r == c else 0 for c in range(9)] for r in range(9)],
        difficulty="hard",
        start_time=now,
        hints_used=2,
        locked_cells=[{"row": 0, "col": 0}],
        is_complete=False,
    )

    data = state.to_dict()
    restored = GameState.from_dict(data)

    assert restored.board == state.board
    assert restored.difficulty == state.difficulty
    assert restored.start_time == state.start_time
    assert restored.hints_used == state.hints_used
    assert restored.locked_cells == state.locked_cells
    assert restored.is_complete == state.is_complete


def test_game_state_from_dict_with_missing_values():
    data = {
        "board": [[0] * 9 for _ in range(9)],
        "difficulty": "easy",
    }

    restored = GameState.from_dict(data)

    assert restored.difficulty == "easy"
    assert restored.start_time is None
    assert restored.hints_used == 0
    assert restored.locked_cells == []
    assert restored.is_complete is False
