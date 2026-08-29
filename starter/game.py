import time

from validation import find_incorrect_cells


_GAME_TIMES = {}


def start_game(current, clues, generate_puzzle):
    puzzle, solution = generate_puzzle(clues)
    current['puzzle'] = puzzle
    current['solution'] = solution
    current['hints_used'] = 0
    _GAME_TIMES[id(current)] = {
        'started_at': time.monotonic(),
        'elapsed_seconds': None,
    }
    return puzzle


def complete_game(current):
    timing = _GAME_TIMES.get(id(current))
    if timing is None:
        return None
    if timing['elapsed_seconds'] is None:
        timing['elapsed_seconds'] = int(time.monotonic() - timing['started_at'])
    return timing['elapsed_seconds']


def check_board(current, board):
    solution = current.get('solution')
    if solution is None:
        return None

    incorrect = find_incorrect_cells(board, solution)
    puzzle = current.get('puzzle')
    if puzzle is not None:
        for row in range(len(puzzle)):
            for col in range(len(puzzle[row])):
                if puzzle[row][col] != 0 and board[row][col] != puzzle[row][col]:
                    if [row, col] not in incorrect:
                        incorrect.append([row, col])
    return incorrect


def get_hint(current, board):
    puzzle = current.get('puzzle')
    solution = current.get('solution')
    if puzzle is None or solution is None:
        return None

    for row in range(len(puzzle)):
        for col in range(len(puzzle[row])):
            if puzzle[row][col] == 0 and board[row][col] == 0:
                current['hints_used'] = current.get('hints_used', 0) + 1
                return {
                    'row': row,
                    'col': col,
                    'value': solution[row][col],
                    'hints_used': current['hints_used'],
                }
    return None
