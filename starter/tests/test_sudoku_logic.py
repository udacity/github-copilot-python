import copy
import sys
import os

# Ensure the starter package directory is importable (tests located in starter/tests)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sudoku_logic


def test_constants_and_create_empty_board():
    assert sudoku_logic.SIZE == 9
    assert sudoku_logic.EMPTY == 0
    board = sudoku_logic.create_empty_board()
    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_deep_copy_independent():
    orig = sudoku_logic.create_empty_board()
    orig[0][0] = 1
    cp = sudoku_logic.deep_copy(orig)
    assert cp == orig
    cp[0][0] = 2
    # original should remain unchanged
    assert orig[0][0] == 1


def test_is_safe_row_column_subgrid():
    b = sudoku_logic.create_empty_board()
    # row conflict
    b[0][1] = 5
    assert sudoku_logic.is_safe(b, 0, 2, 5) is False
    # column conflict
    b[1][2] = 6
    assert sudoku_logic.is_safe(b, 0, 2, 6) is False
    # 3x3 subgrid conflict
    b[1][1] = 7
    assert sudoku_logic.is_safe(b, 2, 2, 7) is False
    # a safe number
    assert sudoku_logic.is_safe(b, 0, 0, 9) is True


def _is_valid_complete_board(board):
    SIZE = sudoku_logic.SIZE
    # rows
    for r in range(SIZE):
        row_vals = sorted(board[r])
        assert row_vals == list(range(1, SIZE + 1))
    # cols
    for c in range(SIZE):
        col_vals = sorted(board[r][c] for r in range(SIZE))
        assert col_vals == list(range(1, SIZE + 1))
    # 3x3 boxes
    for br in range(0, SIZE, 3):
        for bc in range(0, SIZE, 3):
            vals = []
            for r in range(3):
                for c in range(3):
                    vals.append(board[br + r][bc + c])
            assert sorted(vals) == list(range(1, SIZE + 1))


def test_fill_board_completes_board():
    b = sudoku_logic.create_empty_board()
    assert sudoku_logic.fill_board(b) is True
    # no zeros left
    assert all(cell != sudoku_logic.EMPTY for row in b for cell in row)
    # board validity checks
    _is_valid_complete_board(b)


def test_generate_puzzle_has_requested_clues_and_solution_full():
    clues = 30
    puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    # puzzle clues count
    non_empty = sum(1 for r in puzzle for c in r if c != sudoku_logic.EMPTY)
    assert non_empty == clues
    # solution is full (no empty cells)
    assert all(cell != sudoku_logic.EMPTY for row in solution for cell in row)
    # wherever puzzle has a clue, it must match solution
    for r in range(sudoku_logic.SIZE):
        for c in range(sudoku_logic.SIZE):
            if puzzle[r][c] != sudoku_logic.EMPTY:
                assert puzzle[r][c] == solution[r][c]


def test_all_difficulties_generate_unique_puzzles_with_distinct_clue_counts():
    clue_counts = {}
    for difficulty in ['easy', 'medium', 'hard']:
        puzzle, solution = sudoku_logic.generate_puzzle_for_difficulty(difficulty)
        non_empty = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
        clue_counts[difficulty] = non_empty
        assert non_empty == sudoku_logic.DIFFICULTY_SETTINGS[difficulty]['clues']
        assert sudoku_logic.count_solutions(puzzle) == 1
        assert all(cell != sudoku_logic.EMPTY for row in solution for cell in row)

    assert clue_counts['easy'] > clue_counts['medium'] > clue_counts['hard']


def test_generate_puzzle_for_invalid_difficulty_raises_error():
    try:
        sudoku_logic.generate_puzzle_for_difficulty('impossible')
        assert False, 'Expected ValueError for invalid difficulty'
    except ValueError:
        pass


def test_find_incorrect_cells_detects_invalid_entries():
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    board = sudoku_logic.deep_copy(solution)
    board[0][0] = 9
    assert sudoku_logic.find_incorrect_cells(board, solution) == [[0, 0]]


def test_is_board_solved_recognizes_completed_solution():
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    assert sudoku_logic.is_board_solved(solution, solution) is True

    incomplete = sudoku_logic.deep_copy(solution)
    incomplete[0][0] = sudoku_logic.EMPTY
    assert sudoku_logic.is_board_solved(incomplete, solution) is False


def test_count_solutions_unique_puzzle():
    puzzle = [
        [5,3,0,0,7,0,0,0,0],
        [6,0,0,1,9,5,0,0,0],
        [0,9,8,0,0,0,0,6,0],
        [8,0,0,0,6,0,0,0,3],
        [4,0,0,8,0,3,0,0,1],
        [7,0,0,0,2,0,0,0,6],
        [0,6,0,0,0,0,2,8,0],
        [0,0,0,4,1,9,0,0,5],
        [0,0,0,0,8,0,0,7,9],
    ]
    assert sudoku_logic.count_solutions(puzzle) == 1


def test_count_solutions_multiple_solutions():
    empty_board = sudoku_logic.create_empty_board()
    assert sudoku_logic.count_solutions(empty_board, limit=2) == 2


def test_generate_puzzle_has_unique_solution():
    for _ in range(10):
        puzzle, solution = sudoku_logic.generate_puzzle(clues=35)
        assert sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY) == 35
        assert sudoku_logic.count_solutions(puzzle) == 1
        assert all(cell != sudoku_logic.EMPTY for row in solution for cell in row)
        for r in range(sudoku_logic.SIZE):
            for c in range(sudoku_logic.SIZE):
                if puzzle[r][c] != sudoku_logic.EMPTY:
                    assert puzzle[r][c] == solution[r][c]


def test_fill_board_solves_known_puzzle():
    puzzle = [
        [5,3,0,0,7,0,0,0,0],
        [6,0,0,1,9,5,0,0,0],
        [0,9,8,0,0,0,0,6,0],
        [8,0,0,0,6,0,0,0,3],
        [4,0,0,8,0,3,0,0,1],
        [7,0,0,0,2,0,0,0,6],
        [0,6,0,0,0,0,2,8,0],
        [0,0,0,4,1,9,0,0,5],
        [0,0,0,0,8,0,0,7,9],
    ]
    expected = [
        [5,3,4,6,7,8,9,1,2],
        [6,7,2,1,9,5,3,4,8],
        [1,9,8,3,4,2,5,6,7],
        [8,5,9,7,6,1,4,2,3],
        [4,2,6,8,5,3,7,9,1],
        [7,1,3,9,2,4,8,5,6],
        [9,6,1,5,3,7,2,8,4],
        [2,8,7,4,1,9,6,3,5],
        [3,4,5,2,8,6,1,7,9],
    ]
    b = copy.deepcopy(puzzle)
    assert sudoku_logic.fill_board(b) is True
    assert b == expected
