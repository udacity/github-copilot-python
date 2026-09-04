import copy
import random

SIZE = 9
EMPTY = 0


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3

    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False

    return True


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)

                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate

                        if fill_board(board):
                            return True

                        board[row][col] = EMPTY

                return False

    return True


def count_solutions(board, limit=2):
    """Return the number of solutions, capped at limit."""
    solutions = 0

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                for candidate in range(1, SIZE + 1):
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        solutions += count_solutions(board, limit)

                        board[row][col] = EMPTY

                        if solutions >= limit:
                            return solutions

                return solutions

    return 1


def remove_cells(board, clues):
    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError("clues must be between 0 and 81")

    positions = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
        if board[row][col] != EMPTY
    ]
    random.shuffle(positions)

    for row, col in positions:
        if sum(
            cell != EMPTY
            for current_row in board
            for cell in current_row
        ) <= clues:
            break

        value = board[row][col]
        board[row][col] = EMPTY

        if count_solutions(board) != 1:
            board[row][col] = value

DIFFICULTY_CLUES = {
    "easy": 45,
    "medium": 35,
    "hard": 25,
}


def clue_count_for_difficulty(difficulty):
    try:
        return DIFFICULTY_CLUES[difficulty.lower()]
    except (AttributeError, KeyError):
        raise ValueError(
            "difficulty must be easy, medium, or hard"
        )

def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)

    solution = deep_copy(board)
    remove_cells(board, clues)

    puzzle = deep_copy(board)
    return puzzle, solution