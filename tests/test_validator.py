from utils.validator import SudokuValidator


def test_is_valid_move_returns_true_for_empty_cell():
    board = [[0] * 9 for _ in range(9)]
    valid, details = SudokuValidator.is_valid_move(board, 0, 0, 5)

    assert valid is True
    assert details["errors"] == []
    assert details["row_conflict"] is False
    assert details["col_conflict"] is False
    assert details["box_conflict"] is False


def test_is_valid_move_detects_row_conflict():
    board = [[0] * 9 for _ in range(9)]
    board[0][1] = 7

    valid, details = SudokuValidator.is_valid_move(board, 0, 0, 7)

    assert valid is False
    assert "Duplicate value found in row." in details["errors"]
    assert details["row_conflict"] is True


def test_is_valid_move_detects_column_conflict():
    board = [[0] * 9 for _ in range(9)]
    board[1][0] = 4

    valid, details = SudokuValidator.is_valid_move(board, 0, 0, 4)

    assert valid is False
    assert "Duplicate value found in column." in details["errors"]
    assert details["col_conflict"] is True


def test_is_valid_move_detects_box_conflict():
    board = [[0] * 9 for _ in range(9)]
    board[1][1] = 9

    valid, details = SudokuValidator.is_valid_move(board, 0, 0, 9)

    assert valid is False
    assert "Duplicate value found in 3x3 box." in details["errors"]
    assert details["box_conflict"] is True


def test_find_conflicts_returns_duplicate_entries():
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 5
    board[0][3] = 5
    board[1][0] = 5
    board[3][3] = 5

    conflicts = SudokuValidator.find_conflicts(board)

    assert any(conflict["type"] == "row" and conflict["index"] == 0 for conflict in conflicts)
    assert any(conflict["type"] == "column" and conflict["index"] == 0 for conflict in conflicts)
    assert any(conflict["type"] == "box" and conflict["box_row"] == 0 and conflict["box_col"] == 0 for conflict in conflicts)


def test_check_completion_reports_missing_cells_and_conflicts():
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 1
    board[0][1] = 1

    result = SudokuValidator.check_completion(board)

    assert result["is_complete"] is False
    assert result["is_valid_solution"] is False
    assert len(result["missing_cells"]) == 9 * 9 - 2
    assert len(result["conflicts"]) > 0


def test_check_completion_returns_valid_solution_for_complete_board():
    board = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]

    result = SudokuValidator.check_completion(board)

    assert result["is_complete"] is True
    assert result["is_valid_solution"] is True
    assert result["missing_cells"] == []
    assert result["conflicts"] == []
