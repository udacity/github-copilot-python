import random

from board import EMPTY, SIZE


def _candidates(board, row, col):
    return [
        candidate
        for candidate in range(1, SIZE + 1)
        if is_safe(board, row, col, candidate)
    ]


def _is_valid_partial_board(board):
    for row in range(SIZE):
        values = [value for value in board[row] if value != EMPTY]
        if any(value < 1 or value > SIZE for value in values):
            return False
        if len(values) != len(set(values)):
            return False

    for col in range(SIZE):
        values = [board[row][col] for row in range(SIZE) if board[row][col] != EMPTY]
        if len(values) != len(set(values)):
            return False

    for start_row in range(0, SIZE, 3):
        for start_col in range(0, SIZE, 3):
            values = [
                board[row][col]
                for row in range(start_row, start_row + 3)
                for col in range(start_col, start_col + 3)
                if board[row][col] != EMPTY
            ]
            if len(values) != len(set(values)):
                return False

    return True


def count_solutions(board, limit=2):
    if limit < 1 or not _is_valid_partial_board(board):
        return 0

    count = 0

    def search():
        nonlocal count

        if count >= limit:
            return

        best_cell = None
        best_candidates = None
        for row in range(SIZE):
            for col in range(SIZE):
                if board[row][col] == EMPTY:
                    candidates = _candidates(board, row, col)
                    if not candidates:
                        return
                    if best_candidates is None or len(candidates) < len(best_candidates):
                        best_cell = (row, col)
                        best_candidates = candidates

        if best_cell is None:
            count += 1
            return

        row, col = best_cell
        for candidate in best_candidates:
            board[row][col] = candidate
            search()
            board[row][col] = EMPTY
            if count >= limit:
                return

    search()
    return count


def is_safe(board, row, col, num):
    for index in range(SIZE):
        if board[row][index] == num or board[index][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3
    for box_row in range(3):
        for box_col in range(3):
            if board[start_row + box_row][start_col + box_col] == num:
                return False
    return True


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                candidates = list(range(1, SIZE + 1))
                random.shuffle(candidates)
                for candidate in candidates:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True
