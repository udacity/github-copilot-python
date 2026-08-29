import random

import pytest
import sudoku_logic


def test_create_empty_board_has_nine_rows_of_nine_empty_cells():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert sudoku_logic.is_safe(board, 0, 1, 5) is False
    assert sudoku_logic.is_safe(board, 1, 0, 5) is False
    assert sudoku_logic.is_safe(board, 1, 1, 5) is False
    assert sudoku_logic.is_safe(board, 1, 1, 4) is True


def test_fill_board_creates_a_complete_valid_solution():
    random.seed(0)
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board) is True
    assert all(
        set(row) == set(range(1, sudoku_logic.SIZE + 1))
        for row in board
    )
    assert all(
        {board[row][col] for row in range(sudoku_logic.SIZE)}
        == set(range(1, sudoku_logic.SIZE + 1))
        for col in range(sudoku_logic.SIZE)
    )
    assert all(
        {
            board[row][col]
            for row in range(box_row, box_row + 3)
            for col in range(box_col, box_col + 3)
        }
        == set(range(1, sudoku_logic.SIZE + 1))
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_col in range(0, sudoku_logic.SIZE, 3)
    )


def test_count_solutions_returns_one_for_a_complete_valid_board():
    board = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(board)

    assert sudoku_logic.count_solutions(board) == 1


def test_count_solutions_stops_at_two_for_an_ambiguous_board():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.count_solutions(board) == 2


def test_count_solutions_returns_zero_for_an_invalid_board():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 1

    assert sudoku_logic.count_solutions(board) == 0


def test_count_solutions_does_not_mutate_the_board():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    original = [row[:] for row in board]

    sudoku_logic.count_solutions(board)

    assert board == original


def test_generate_puzzle_returns_solution_and_requested_number_of_clues():
    random.seed(1)

    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35
    assert all(
        puzzle[row][col] == sudoku_logic.EMPTY
        or puzzle[row][col] == solution[row][col]
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )
    assert sudoku_logic.count_solutions(puzzle) == 1


def test_generated_puzzles_are_unique_for_multiple_random_seeds():
    for seed in range(3):
        random.seed(seed)
        puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

        assert sudoku_logic.count_solutions(puzzle) == 1
        assert all(
            puzzle[row][col] == sudoku_logic.EMPTY
            or puzzle[row][col] == solution[row][col]
            for row in range(sudoku_logic.SIZE)
            for col in range(sudoku_logic.SIZE)
        )


def test_difficulty_levels_have_strictly_different_clue_counts_and_unique_solutions():
    clue_counts = {}

    for difficulty in ('easy', 'medium', 'hard'):
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
        clue_counts[difficulty] = sum(
            cell != sudoku_logic.EMPTY for row in puzzle for cell in row
        )

        assert clue_counts[difficulty] == sudoku_logic.DIFFICULTY_CLUES[difficulty]
        assert sudoku_logic.count_solutions(puzzle) == 1
        assert all(
            puzzle[row][col] == sudoku_logic.EMPTY
            or puzzle[row][col] == solution[row][col]
            for row in range(sudoku_logic.SIZE)
            for col in range(sudoku_logic.SIZE)
        )

    assert clue_counts['easy'] > clue_counts['medium'] > clue_counts['hard']


def test_generate_puzzle_rejects_unknown_difficulty():
    with pytest.raises(ValueError, match='difficulty'):
        sudoku_logic.generate_puzzle(difficulty='expert')
