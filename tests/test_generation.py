from utils.generation import SudokuGenerator


def test_generate_puzzle_returns_expected_dimensions():
    puzzle, solution = SudokuGenerator.generate_puzzle("medium")

    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert len(solution) == 9
    assert all(len(row) == 9 for row in solution)
    assert puzzle != solution


def test_generate_puzzle_invalid_difficulty_raises_value_error():
    try:
        SudokuGenerator.generate_puzzle("unknown")
        raised = False
    except ValueError:
        raised = True

    assert raised is True


def test_generated_puzzle_has_unique_solution():
    puzzle, solution = SudokuGenerator.generate_puzzle("easy")

    assert SudokuGenerator.ensure_unique_solution(puzzle)
    assert solution != [[0] * 9 for _ in range(9)]


def test_generate_puzzle_returns_solution_copy():
    puzzle, solution = SudokuGenerator.generate_puzzle("hard")

    assert SudokuGenerator.ensure_unique_solution(puzzle)
    assert all(1 <= cell <= 9 for row in solution for cell in row)
    # Check that clues are within the hard range (25-28)
    clue_count = sum(cell != 0 for row in puzzle for cell in row)
    assert 25 <= clue_count <= 28


def test_generate_puzzle_easy_clues_in_range():
    puzzle, _ = SudokuGenerator.generate_puzzle("easy")
    clue_count = sum(cell != 0 for row in puzzle for cell in row)
    assert 40 <= clue_count <= 45


def test_generate_puzzle_medium_clues_in_range():
    puzzle, _ = SudokuGenerator.generate_puzzle("medium")
    clue_count = sum(cell != 0 for row in puzzle for cell in row)
    assert 30 <= clue_count <= 35


def test_generate_puzzle_hard_clues_in_range():
    puzzle, _ = SudokuGenerator.generate_puzzle("hard")
    clue_count = sum(cell != 0 for row in puzzle for cell in row)
    assert 25 <= clue_count <= 28
