# Project Instructions

## Project Overview

This project is a Python Flask Sudoku game being refactored from legacy code into a maintainable, responsive, and user-friendly application.

## Code Quality

- Follow clean and readable Python coding practices.
- Follow PEP 8 conventions.
- Use meaningful names for variables, functions, and classes.
- Prefer small, focused, reusable functions.
- Avoid unnecessary code duplication.
- Keep Sudoku game logic separate from Flask route handling where practical.
- Preserve existing working functionality unless a requirement requires changing it.
- Add comments and docstrings where they improve understanding.
- Use consistent error handling.

## Sudoku Requirements

The completed application must:

- Generate valid Sudoku puzzles.
- Ensure every generated puzzle has exactly one unique solution.
- Support Easy, Medium, and Hard difficulty levels.
- Adjust the number of prefilled cells according to difficulty.
- Keep prefilled cells locked.
- Provide immediate visual feedback for invalid moves.
- Display a completion message when the puzzle is solved correctly.

## Game Features

The application must include:

- A Hint button that fills one correct empty cell and locks it.
- A Check button that highlights incorrect entries.
- A timer that tracks the player's solving time.
- A Top 10 scoreboard containing player name, time, difficulty, and number of hints.
- Browser localStorage so Top 10 scores persist between sessions.
- A dark mode toggle.

## UI and Styling

- Keep the interface clean and consistent.
- Support both light and dark modes.
- Make the layout responsive for desktop and mobile screens.
- Use alternating colors for the 3x3 Sudoku blocks.
- Keep text, buttons, and controls readable.
- Avoid unnecessary layout shifts.

## Testing

- Establish the testing framework before refactoring the application.
- Preserve existing behavior during refactoring.
- Run tests after every major refactor or feature update.
- Do not remove or weaken tests just to make them pass.
- Investigate the underlying cause of test failures.

## Copilot Usage

- Inspect the existing code before making significant changes.
- Start with the larger architectural problems before smaller refinements.
- Prefer incremental and focused changes.
- Do not rewrite working code unnecessarily.
- Evaluate Copilot-generated suggestions before accepting them.
- Reject or modify suggestions that introduce unnecessary complexity.
- Prefer simple solutions that satisfy the project requirements.
- Explain unfamiliar generated code before relying on it.

## Documentation

- Keep the README updated with setup and testing instructions.
- Document the command required to run the test suite.
- Store required Copilot screenshots in the Screenshots folder.
- Never include passwords, API keys, or other sensitive information in the repository.