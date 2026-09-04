import sudoku_logic


def is_valid_solution(board):
    expected = set(range(1, sudoku_logic.SIZE + 1))

    rows_valid = all(set(row) == expected for row in board)
    columns_valid = all(
        {board[row][column] for row in range(sudoku_logic.SIZE)} == expected
        for column in range(sudoku_logic.SIZE)
    )

    boxes_valid = all(
        {
            board[row][column]
            for row in range(box_row, box_row + 3)
            for column in range(box_column, box_column + 3)
        }
        == expected
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_column in range(0, sudoku_logic.SIZE, 3)
    )

    return rows_valid and columns_valid and boxes_valid


def test_create_empty_board():
    board = sudoku_logic.create_empty_board()

    assert len(board) == 9
    assert all(len(row) == 9 for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_rejects_row_conflict():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 0, 1, 5)


def test_is_safe_rejects_column_conflict():
    board = sudoku_logic.create_empty_board()
    board[1][1] = 6

    assert not sudoku_logic.is_safe(board, 0, 1, 6)


def test_is_safe_rejects_box_conflict():
    board = sudoku_logic.create_empty_board()
    board[1][1] = 7

    assert not sudoku_logic.is_safe(board, 0, 0, 7)


def test_is_safe_accepts_valid_candidate():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.is_safe(board, 0, 0, 1)


def test_fill_board_fills_board_in_place():
    board = sudoku_logic.create_empty_board()

    result = sudoku_logic.fill_board(board)

    assert result is True
    assert is_valid_solution(board)


def test_generate_puzzle_returns_puzzle_and_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert len(puzzle) == 9
    assert len(solution) == 9
    assert is_valid_solution(solution)

    assert sum(
        cell != sudoku_logic.EMPTY
        for row in puzzle
        for cell in row
    ) == 35

    for row in range(9):
        for column in range(9):
            if puzzle[row][column] != sudoku_logic.EMPTY:
                assert puzzle[row][column] == solution[row][column]
def test_count_solutions_returns_one_for_generated_puzzle():
    puzzle, _ = sudoku_logic.generate_puzzle(clues=35)

    assert sudoku_logic.count_solutions(puzzle) == 1


def test_count_solutions_stops_at_two_for_empty_board():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.count_solutions(board) == 2


def test_remove_cells_preserves_requested_clue_count_and_uniqueness():
    board = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(board)

    sudoku_logic.remove_cells(board, clues=35)

    assert sum(
        cell != sudoku_logic.EMPTY
        for row in board
        for cell in row
    ) == 35
    assert sudoku_logic.count_solutions(board) == 1

import pytest


@pytest.mark.parametrize(
    ("difficulty", "expected_clues"),
    [
        ("easy", 45),
        ("medium", 35),
        ("hard", 25),
    ],
)
def test_clue_count_for_difficulty(difficulty, expected_clues):
    assert (
        sudoku_logic.clue_count_for_difficulty(difficulty)
        == expected_clues
    )


def test_clue_count_for_difficulty_rejects_invalid_value():
    with pytest.raises(ValueError):
        sudoku_logic.clue_count_for_difficulty("expert")