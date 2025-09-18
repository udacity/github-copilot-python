# Refactor a Simple Sudoku Game written in Python

Use this simple Sudoku game as a starting point to practice your skills with GitHub Copilot. 
The goal is to refactor the code to use modern technologies, while also adding new features and improving the overall user experience.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Dependencies

```
- Modern web browser (Chrome, Firefox, Edge, etc.)
- Python 3
```

### Installation

1. Fork this repository to your GitHub account. Use the "Fork" button on the top right corner of the repository page.

2. Clone your forked repository to your local machine.

3. Create a virtualenv and activate it (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install all requirements:

```bash
pip install -r requirements.txt
```

5. Run the Flask app:

```bash
python app.py
```

6. Open http://127.0.0.1:5000 in your browser.

## Project Instructions

Use GitHub Copilot to refactor the code for this game to add more advanced features. The goal is to create a more modern and maintainable codebase and add additional functionality to the final product. You can use any combination of code completion and chat features, like Ask, Edit, or Agent modes.

- Errors should be handled gracefully with appropriate messages to the user.
- Implement a Sudoku board generator that creates a valid Sudoku puzzle with a unique solution.
- Add a timer to track how long it takes to solve the puzzle.
- Implement a solution checker that verifies if the user's solution is correct using event delegation.
- Add a difficulty selector to allow users to choose between easy, medium, and hard puzzles.
- Implement a New Game button to start a new game without refreshing the page.
- Add a hint feature that provides clues for the user that are noted with unique colors.
- Add a check puzzle button that checks the current state of the board against the solution.
- User should get immediate feedback on their input, such as highlighting invalid entries.
- Top 10 scores should be saved in local storage and displayed on the page with the user's name, time taken, hints used, and difficulty level.
- The game should be responsive and work well on both desktop and mobile devices.
- UI colors should be visually appealing and accessible.
- Completed and correct puzzles should display a congratulatory message with the time taken and hints used and ask for the user's name for Top 10 times.
