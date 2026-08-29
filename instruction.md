# GitHub Copilot Instructions — Flask Sudoku Project

## Project Overview

This project is a Python Flask Sudoku game that is being refactored from legacy code into a modern, modular, maintainable application.

The application should provide:
- Sudoku puzzle generation
- Unique-solution validation
- Easy, Medium, and Hard difficulty levels
- Locked prefilled cells
- Immediate input validation
- Check Puzzle functionality
- Hint functionality
- Puzzle completion detection
- Timer
- Top 10 leaderboard
- Browser localStorage persistence
- Light and dark modes
- Responsive desktop and mobile layouts
- Accessible user interface

## General Coding Standards

- Use modern Python practices.
- Keep code readable, maintainable, and modular.
- Use clear and descriptive variable, function, and class names.
- Keep functions focused on a single responsibility.
- Avoid unnecessary duplication.
- Avoid unnecessary dependencies.
- Preserve existing functionality when refactoring.
- Do not modify unrelated files or features.
- Prefer simple and understandable solutions over unnecessarily complex implementations.
- Handle errors gracefully.
- Provide clear user-facing error and status messages.
- Add comments only where they improve understanding of non-obvious logic.

## Application Architecture

Keep responsibilities separated.

Prefer the following separation:

- Flask routes handle HTTP requests and responses.
- Sudoku generation handles puzzle creation.
- Sudoku solving handles solution finding and solution counting.
- Validation handles Sudoku rule validation and user input checking.
- Frontend HTML handles page structure.
- CSS handles styling, themes, responsiveness, and visual states.
- JavaScript handles client-side interaction and dynamic UI behavior.
- Leaderboard functionality handles localStorage persistence and score management.

Avoid putting all application logic into one large Flask file.

## Sudoku Requirements

- Every generated Sudoku puzzle must be valid.
- Every generated puzzle must have exactly one solution.
- The solution must be verified before the puzzle is presented to the player.
- Easy, Medium, and Hard must have different numbers of prefilled cells.
- Easy should provide more clues than Medium.
- Medium should provide more clues than Hard.
- Prefilled cells must be locked and must not be editable.
- Hint-filled cells must also become locked.
- User-entered values must be validated.
- Incorrect entries must receive clear visual feedback.
- Completed puzzles must be detected correctly.

## Game Features

### Difficulty

Support:
- Easy
- Medium
- Hard

Changing difficulty should start an appropriate new puzzle.

### Hint

- Fill one correct empty cell.
- Never overwrite a user's existing value.
- Visually distinguish the hinted cell.
- Lock the hinted cell.
- Track the number of hints used.

### Check Puzzle

- Check the current board against the correct solution.
- Highlight incorrect entries.
- Do not incorrectly mark valid entries.
- Use event delegation where required by the project.

### Timer

- Start the timer when a new puzzle begins.
- Display elapsed time clearly.
- Stop the timer when the puzzle is correctly completed.
- Reset the timer for a new puzzle.

### Leaderboard

Store the Top 10 scores in browser localStorage.

Each score should contain:
- Player name
- Completion time
- Difficulty
- Number of hints used

Sort scores by fastest completion time and keep only the best 10 scores.

Handle missing or corrupted localStorage data gracefully.

## Frontend and Accessibility

- Use semantic HTML where appropriate.
- Ensure controls have clear labels.
- Ensure buttons are keyboard accessible.
- Provide visible focus states.
- Maintain readable text and controls.
- Maintain sufficient color contrast.
- Do not rely only on color to communicate important information.
- Provide clear feedback for errors and successful actions.
- Ensure dark mode remains readable and accessible.
- Ensure the layout works on desktop, tablet, and mobile.
- Avoid horizontal scrolling where possible.
- Ensure the Sudoku grid does not shift when styles or states change.
- Use alternating visual styles for the 3x3 Sudoku regions.

## Testing

- Use pytest for Python tests where appropriate.
- Run tests after every major change.
- Do not remove or weaken tests simply to make them pass.
- Add tests for important Sudoku logic and new functionality where practical.
- Preserve existing behavior during refactoring.

## GitHub Copilot Usage

Before implementing a major change:
1. Analyze the existing code.
2. Propose an approach.
3. Explain which files will change.
4. Wait for approval before making significant changes.

When reviewing Copilot suggestions:
- Do not blindly accept generated code.
- Check whether the approach is necessary and maintainable.
- Reject unnecessary dependencies.
- Reject unnecessarily complex implementations.
- Prefer the simplest solution that satisfies the requirements.

Do not rebuild the entire application when only a focused change is required.

## Change Management

- Make small, focused changes.
- Avoid unrelated modifications.
- Preserve completed features when adding new functionality.
- Run tests after changes.
- Verify the application manually after major changes.
- If a change causes a regression, identify and fix the root cause instead of removing functionality.