# Project Instructions

This project should be refactored into a clean, modern Python Flask application using best practices and modular architecture.

## Requirements

- Target Python 3.10 or newer.
- Use Flask application patterns with clearly separated routes, services, and templates.
- Separate game logic from web adapters.
- Use a Hexagonal architecture style with:
  - Ports: core game interfaces and abstractions
  - Adapters: Flask routes, JSON I/O, HTML templates
- Keep modules small, single-purpose, and easy to test.
- Follow PEP 8 style and naming conventions.
- Use type hints throughout the codebase.
- Add docstrings for functions, classes, and modules.
- Use consistent error handling for invalid input and missing game state.
- Prefer modern Python language features where appropriate:
  - f-strings
  - dataclasses
  - context managers
  - `match`/`case` if helpful
  - sequence and dictionary comprehensions
- Keep templates and static files focused on presentation only; do not embed business rules into HTML or JavaScript.

## Architecture Guidance

- Core domain logic belongs in its own package or module, separate from Flask-specific code.
- Web layer should act as an adapter that calls game service ports.
- Templates should render board state but not perform validation logic.
- Keep state management minimal in the Flask app; prefer request-driven operations and explicit adapters.

## Testing and Quality

- Add or extend unit tests for core game logic.
- Add or extend integration tests for Flask routes.
- Ensure tests cover normal flows and error conditions.
- Keep test fixtures isolated and reusable.

## Example Structure

- `starter/app.py` or `starter/server.py` — Flask application setup and routes
- `starter/ports.py` — service interfaces or abstractions for game operations
- `starter/adapters/` — Flask route adapters, persistence adapters, JSON adapters
- `starter/domain/` — game logic, board generation, validation, solver
- `starter/templates/` — HTML templates
- `starter/static/` — CSS and JavaScript

## Deliverables

- A refactored codebase that is easier to maintain and extend.
- Clear separation between domain logic and Flask application code.
- A consistent, idiomatic Python style with type hints and documentation.
- A testable application with pytest support.

## Resources

- [Hexagonal Architecture](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
- [PEP 8 Style Guide](https://pep8.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)