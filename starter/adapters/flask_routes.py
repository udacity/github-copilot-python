"""Flask HTTP routes adapter.

This module adapts the Flask web framework to the game service,
converting HTTP requests/responses to/from domain objects.
"""

from datetime import datetime
from typing import Any

from flask import Blueprint, jsonify, render_template, request

from ports.game_service import GameServicePort
from ports.scoreboard_repository import ScoreboardRepository
from utils.validator import SudokuValidator


class FlaskRoutesAdapter:
    """Adapter for Flask HTTP routes to game service.

    Handles HTTP request/response conversion and error handling
    for the game service.
    """

    def __init__(self, game_service: GameServicePort, scoreboard_repo: ScoreboardRepository) -> None:
        """Initialize the Flask routes adapter.

        Args:
            game_service: The game service to use for operations
            scoreboard_repo: The scoreboard repository for persistence
        """
        self.game_service = game_service
        self.scoreboard_repo = scoreboard_repo
        self.blueprint = Blueprint("sudoku", __name__)
        self._register_routes()

    def _register_routes(self) -> None:
        """Register all Flask routes."""
        self.blueprint.route("/")(self._index)
        self.blueprint.route("/new", methods=["GET"])(self._new_game)
        self.blueprint.route("/check", methods=["POST"])(self._check_solution)
        self.blueprint.route("/validate", methods=["POST"])(self._validate_board)
        self.blueprint.route("/check-complete", methods=["POST"])(self._check_complete)
        self.blueprint.route("/hint", methods=["POST"])(self._request_hint)
        self.blueprint.route("/scores", methods=["GET"])(self._get_scores)
        self.blueprint.route("/scores", methods=["POST"])(self._save_score)

    def _index(self) -> str:
        """Render the main game page.

        Returns:
            Rendered HTML template
        """
        return render_template("index.html")

    def _get_json_request(self) -> dict[str, Any] | None:
        """Parse JSON from the request and return a dictionary or None."""
        return request.get_json(silent=True)

    def _json_error(self, message: str, status: int = 400) -> tuple[Any, int]:
        """Build a JSON error response."""
        return jsonify({"error": message}), status

    def _get_request_board(
        self, *, allow_missing: bool = False
    ) -> tuple[list[list[int]] | None, tuple[Any, int] | None]:
        """Extract and validate a board from the JSON request body."""
        data = self._get_json_request()
        if not data or "board" not in data:
            if allow_missing:
                return None, None
            return None, self._json_error("Missing board in request")

        board = data["board"]
        if not self._validate_board_format(board):
            return None, self._json_error("Invalid board format")

        return board, None

    def _new_game(self) -> tuple[Any, int]:
        """Create a new game puzzle.

        Query parameters:
            difficulty: Difficulty level ('easy', 'medium', 'hard'). Default 'medium'.
            clues: Exact number of clues (1-81). Optional.

        Returns:
            JSON response with puzzle grid and locked cells
        """
        try:
            clues_param = request.args.get("clues")
            difficulty = request.args.get("difficulty", "medium")

            if clues_param is not None:
                try:
                    clues = int(clues_param)
                except ValueError:
                    return jsonify({"error": "Clues must be an integer."}), 400

                if not (1 <= clues <= 81):
                    return jsonify({"error": "Clues must be between 1 and 81"}), 400

                puzzle = self.game_service.new_game(clues=clues)
            else:
                if difficulty not in ["easy", "medium", "hard"]:
                    return jsonify({"error": "Difficulty must be easy, medium, or hard"}), 400

                puzzle = self.game_service.new_game(difficulty=difficulty)

            locked_cells = self.game_service.get_locked_cells()
            return jsonify({"puzzle": puzzle, "locked_cells": locked_cells}), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Failed to generate puzzle"}), 500

    def _check_solution(self) -> tuple[Any, int]:
        """Check the user's solution attempt.

        JSON body:
            {
                "board": [[...], [...], ...]  # 9x9 grid
            }

        Returns:
            JSON response with incorrect cells and completion status
        """
        try:
            if not self.game_service.has_active_game():
                return self._json_error("No game in progress")

            board, error_response = self._get_request_board()
            if error_response is not None:
                return error_response

            incorrect, is_complete = self.game_service.check_solution(board)

            return (
                jsonify(
                    {"incorrect": incorrect, "complete": is_complete}
                ),
                200,
            )

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except RuntimeError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Failed to check solution"}), 500

    def _validate_board(self) -> tuple[Any, int]:
        """Validate a board and return any conflicts."""
        try:
            board, error_response = self._get_request_board()
            if error_response is not None:
                return error_response

            conflicts = SudokuValidator.find_conflicts(board)
            return jsonify({"conflicts": conflicts}), 200

        except Exception:
            return jsonify({"error": "Failed to validate board"}), 500

    def _check_complete(self) -> tuple[Any, int]:
        """Check if the board is completely and correctly solved."""
        try:
            board, error_response = self._get_request_board()
            if error_response is not None:
                return error_response

            completion_result = SudokuValidator.check_completion(board)
            
            is_complete = completion_result["is_complete"]
            is_valid = completion_result["is_valid_solution"]
            
            if is_complete and is_valid:
                message = "Congratulations! You solved the puzzle correctly!"
            elif is_complete and not is_valid:
                message = "Board is complete but contains errors."
            else:
                message = "Board is not yet complete."

            # Get game statistics
            stats = self.game_service.get_game_stats()

            return jsonify({
                "is_complete": is_complete and is_valid,
                "message": message,
                "elapsed_time": stats["elapsed_time"],
                "difficulty": stats["difficulty"],
                "hints_used": stats["hints_used"]
            }), 200

        except Exception:
            return jsonify({"error": "Failed to check completion"}), 500

    def _request_hint(self) -> tuple[Any, int]:
        """Provide a hint by filling a random empty cell and locking it."""
        try:
            if not self.game_service.has_active_game():
                return self._json_error("No game in progress")

            board, error_response = self._get_request_board(allow_missing=True)
            if error_response is not None:
                return error_response

            hint = self.game_service.hint(board)
            return jsonify(hint), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except RuntimeError as e:
            return jsonify({"error": str(e)}), 400
        except Exception:
            return jsonify({"error": "Failed to provide hint"}), 500

    def _get_scores(self) -> tuple[Any, int]:
        """Return the top 10 scores from the server."""
        try:
            scores = self.scoreboard_repo.get_top_scores(10)
            score_list = [self._serialize_score(score) for score in scores]
            return jsonify({"scores": score_list}), 200
        except Exception:
            return jsonify({"error": "Failed to retrieve scores"}), 500

    def _save_score(self) -> tuple[Any, int]:
        """Save a new score to the server."""
        try:
            data = self._get_json_request()
            if not data:
                return self._json_error("Missing score data")

            name = data.get("name", "").strip()
            time = data.get("elapsed_time")
            difficulty = data.get("difficulty", "").strip()
            hints = data.get("hints_used")

            if not isinstance(time, int) or time < 0:
                return self._json_error("Invalid time")
            if not isinstance(hints, int) or hints < 0:
                return self._json_error("Invalid hints")

            try:
                self.scoreboard_repo.add_score(
                    name,
                    time,
                    difficulty,
                    hints,
                    datetime.utcnow().isoformat(),
                )
                self.scoreboard_repo.save()
                return jsonify({"success": True}), 200
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        except Exception:
            return jsonify({"error": "Failed to save score"}), 500

    @staticmethod
    def _serialize_score(score: tuple[str, int, str, int, str]) -> dict[str, Any]:
        """Convert a repository score tuple into a JSON-friendly dictionary."""
        name, time, difficulty, hints, date = score
        return {
            "name": name,
            "elapsed_time": time,
            "difficulty": difficulty,
            "hints_used": hints,
            "date": date,
        }

    @staticmethod
    def _validate_board_format(board: Any) -> bool:
        """Validate that the board has the correct format.

        Args:
            board: The board to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if not isinstance(board, list) or len(board) != 9:
                return False

            for row in board:
                if not isinstance(row, list) or len(row) != 9:
                    return False

                for cell in row:
                    if not isinstance(cell, int) or isinstance(cell, bool) or not (0 <= cell <= 9):
                        return False

            return True
        except (TypeError, IndexError):
            return False
