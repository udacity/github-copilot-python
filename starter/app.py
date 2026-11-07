"""Sudoku game Flask application using Hexagonal Architecture.

This module sets up the Flask application with the game service
and routes using the adapter pattern.
"""

import os
import sys

# Ensure both repo root and starter directory are on sys.path
# This allows imports from sibling packages (adapters, utils, models, config) 
# and from domain subpackages regardless of how the app is executed
try:
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _repo_root = os.path.dirname(_current_dir)
    
    for _path in [_repo_root, _current_dir]:
        if _path not in sys.path:
            sys.path.insert(0, _path)
finally:
    del _current_dir, _repo_root, _path

from flask import Flask

from adapters.flask_routes import FlaskRoutesAdapter
from domain.game import GameService
from ports.scoreboard_repository import ScoreboardRepository


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Configured Flask app instance
    """
    app = Flask(__name__)

    # Initialize domain services
    game_service = GameService()

    # Initialize repository services
    scoreboard_repo = ScoreboardRepository()
    scoreboard_repo.load()

    # Initialize adapters
    routes_adapter = FlaskRoutesAdapter(game_service, scoreboard_repo)

    # Register routes
    app.register_blueprint(routes_adapter.blueprint)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)