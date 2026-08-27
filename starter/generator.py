import random

from board import EMPTY, SIZE, create_empty_board, deep_copy
from solver import count_solutions, fill_board

DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}


def remove_cells(board, clues):
    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError('clues must be between 0 and 81')

    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)

    for row, col in positions:
        if sum(cell != EMPTY for line in board for cell in line) <= clues:
            break

        value = board[row][col]
        if value == EMPTY:
            continue

        board[row][col] = EMPTY
        if count_solutions(board) != 1:
            board[row][col] = value

    if sum(cell != EMPTY for line in board for cell in line) != clues:
        raise RuntimeError('could not reach the requested clue count')


def generate_puzzle(clues=35, max_attempts=100, difficulty=None):
    if difficulty is not None:
        try:
            clues = DIFFICULTY_CLUES[difficulty.lower()]
        except (AttributeError, KeyError):
            raise ValueError('difficulty must be easy, medium, or hard')

    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError('clues must be between 0 and 81')
    if max_attempts < 1:
        raise ValueError('max_attempts must be positive')

    for _ in range(max_attempts):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)

        try:
            remove_cells(board, clues)
        except RuntimeError:
            continue

        if count_solutions(board) == 1:
            return deep_copy(board), solution

    raise RuntimeError('could not generate a uniquely solvable puzzle')
