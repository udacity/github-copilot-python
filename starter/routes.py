from flask import Blueprint, jsonify, render_template, request

import game


def create_routes(current, sudoku_logic):
    routes = Blueprint('routes', __name__)

    @routes.get('/')
    def index():
        return render_template('index.html')

    @routes.get('/new')
    def new_game():
        difficulty = request.args.get('difficulty')
        if difficulty is not None:
            difficulty = difficulty.lower()
            if difficulty not in sudoku_logic.DIFFICULTY_CLUES:
                return jsonify({'error': 'Difficulty must be easy, medium, or hard'}), 400
            clues = sudoku_logic.DIFFICULTY_CLUES[difficulty]
        else:
            clues = int(request.args.get('clues', 35))
        puzzle = game.start_game(current, clues, sudoku_logic.generate_puzzle)
        return jsonify({'puzzle': puzzle})

    @routes.post('/check')
    def check_solution():
        data = request.json
        board = data.get('board')
        incorrect = game.check_board(current, board)
        if incorrect is None:
            return jsonify({'error': 'No game in progress'}), 400
        response = {'incorrect': incorrect}
        if current.get('puzzle') is not None and not incorrect and all(
            value != 0 for row in board for value in row
        ):
            elapsed_seconds = game.complete_game(current)
            if elapsed_seconds is not None:
                response['elapsed_seconds'] = elapsed_seconds
        return jsonify(response)

    @routes.post('/hint')
    def hint():
        data = request.json or {}
        hint_cell = game.get_hint(current, data.get('board', []))
        if hint_cell is None:
            if current.get('solution') is None:
                return jsonify({'error': 'No game in progress'}), 400
            return jsonify({'error': 'No empty cells remain'}), 400
        return jsonify(hint_cell)

    return routes
