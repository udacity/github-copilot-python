import json

from models.scoreboard import Scoreboard


class FakeStorage:
    def __init__(self) -> None:
        self.data = {}

    def setItem(self, key: str, value: str) -> None:
        self.data[key] = value

    def getItem(self, key: str) -> str:
        return self.data.get(key, "")


def test_add_score_and_get_top_10_ordering():
    board = Scoreboard()

    board.add_score("Alice", 120, "easy", 1)
    board.add_score("Bob", 90, "medium", 0)
    board.add_score("Carol", 180, "hard", 3)

    top_scores = board.get_top_10()

    assert top_scores[0][0] == "Bob"
    assert top_scores[0][1] == 90
    assert top_scores[1][0] == "Alice"
    assert top_scores[2][0] == "Carol"
    assert len(top_scores) == 3


def test_add_score_name_validation():
    board = Scoreboard()

    try:
        board.add_score("", 120, "easy", 1)
        assert False, "Expected ValueError for empty name"
    except ValueError:
        pass

    try:
        board.add_score("a" * 31, 120, "easy", 1)
        assert False, "Expected ValueError for long name"
    except ValueError:
        pass


def test_save_and_load_to_local_storage():
    board = Scoreboard()
    storage = FakeStorage()

    board.add_score("Dana", 75, "easy", 0)
    board.save_to_localStorage(storage=storage)

    other_board = Scoreboard()
    other_board.load_from_localStorage(storage=storage)

    assert other_board.get_top_10()[0][0] == "Dana"
    assert other_board.get_top_10()[0][1] == 75
    assert other_board.get_top_10()[0][2] == "easy"
    assert other_board.get_top_10()[0][3] == 0
    assert isinstance(other_board.get_top_10()[0][4], str)


def test_load_from_local_storage_with_invalid_data_clears_scores(tmp_path):
    fallback_file = tmp_path / "scoreboard_storage.json"
    fallback_file.write_text("invalid json")

    board = Scoreboard()
    board.FALLBACK_FILENAME = str(fallback_file)
    board.load_from_localStorage()

    assert board.get_top_10() == []


def test_save_and_load_fallback_file(tmp_path):
    fallback_file = tmp_path / "scoreboard_storage.json"
    board = Scoreboard()
    board.FALLBACK_FILENAME = str(fallback_file)

    board.add_score("Eve", 200, "hard", 2)
    board.save_to_localStorage()

    loaded = Scoreboard()
    loaded.FALLBACK_FILENAME = str(fallback_file)
    loaded.load_from_localStorage()

    assert loaded.get_top_10()[0][0] == "Eve"
    assert loaded.get_top_10()[0][1] == 200
    assert loaded.get_top_10()[0][2] == "hard"
    assert loaded.get_top_10()[0][3] == 2
