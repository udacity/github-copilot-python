from board import SIZE


def find_incorrect_cells(board, solution):
    incorrect = []
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != solution[row][col]:
                incorrect.append([row, col])
    return incorrect
