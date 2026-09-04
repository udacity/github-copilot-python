# Sudoku Project Instructions

This project is a Flask-based Sudoku application.

Code Style:

- Prefer readability over clever implementations.
- Use modern Python features and type hints where appropriate.
- Keep functions small and focused.
- Avoid duplicated code.
- Follow consistent naming conventions.
- Add comments only when they improve understanding.

Architecture:

- Separate game logic from Flask routes.
- Keep UI, business logic, and persistence concerns isolated.
- Prefer reusable helper functions and classes.

Sudoku Requirements:

- Every generated puzzle must have exactly one solution.
- Support Easy, Medium, and Hard difficulties.
- Prefilled cells must remain locked.
- Invalid moves should provide immediate visual feedback.
- Hint cells should become locked after being filled.
- Maintain a Top 10 leaderboard.
- Persist leaderboard data between sessions.

Frontend Requirements:

- Mobile responsive layout.
- Support light and dark themes.
- Alternate colors for 3x3 Sudoku regions.
- Maintain accessibility and readability.

Testing:

- Use pytest.
- Preserve existing behavior during refactoring.
- Add tests for Sudoku generation and validation logic.=[]p