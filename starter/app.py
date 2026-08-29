from flask import Flask

from routes import create_routes
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints_used': 0,
}

app.register_blueprint(create_routes(CURRENT, sudoku_logic))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)