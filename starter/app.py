from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'difficulty': 'medium'
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium')
    clues = request.args.get('clues')

    try:
        if clues is not None:
            clues = int(clues)
        else:
            clues = sudoku_logic.get_difficulty_clues(difficulty)
        puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
    except ValueError:
        return jsonify({'error': 'Invalid difficulty or clue count'}), 400

    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = difficulty
    return jsonify({'puzzle': puzzle, 'solution': solution, 'difficulty': difficulty, 'clues': clues})


@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = sudoku_logic.find_incorrect_cells(board, solution)
    return jsonify({'incorrect': incorrect})


if __name__ == '__main__':
    app.run(debug=True)