// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_STORAGE_KEY = 'sudokuLeaderboard';
const THEME_STORAGE_KEY = 'sudokuTheme';
const MAX_LEADERBOARD_ENTRIES = 10;
let puzzle = [];
let gameStartedAt = 0;
let timerInterval = null;
let gameCompleted = false;

function applyTheme(theme) {
  const isDark = theme === 'dark';
  document.documentElement.dataset.theme = isDark ? 'dark' : 'light';
  const toggle = document.getElementById('theme-toggle');
  toggle.setAttribute('aria-pressed', String(isDark));
  toggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
  toggle.querySelector('.theme-toggle-label').innerText = isDark ? 'Light mode' : 'Dark mode';
}

function toggleTheme() {
  const nextTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);
  try {
    localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  } catch (error) {
    // Theme preference is optional when storage is unavailable.
  }
}

function getLeaderboard() {
  try {
    const stored = JSON.parse(localStorage.getItem(LEADERBOARD_STORAGE_KEY) || '[]');
    if (!Array.isArray(stored)) return [];
    return stored.filter((entry) => (
      entry && typeof entry.name === 'string' &&
      Number.isFinite(entry.time) && entry.time >= 0 &&
      typeof entry.difficulty === 'string' &&
      Number.isInteger(entry.hints) && entry.hints >= 0
    )).sort((first, second) => first.time - second.time).slice(0, MAX_LEADERBOARD_ENTRIES);
  } catch (error) {
    return [];
  }
}

function renderLeaderboard() {
  const entriesElement = document.getElementById('leaderboard-entries');
  const emptyElement = document.getElementById('leaderboard-empty');
  entriesElement.innerHTML = '';
  const entries = getLeaderboard();
  emptyElement.hidden = entries.length > 0;
  entries.forEach((entry, index) => {
    const row = document.createElement('tr');
    [index + 1, entry.name, formatTime(entry.time), entry.difficulty, entry.hints].forEach((value) => {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.appendChild(cell);
    });
    entriesElement.appendChild(row);
  });
}

function addLeaderboardScore(time, difficulty, hints) {
  const name = window.prompt('Enter your name for the leaderboard:');
  const score = {
    name: name && name.trim() ? name.trim().slice(0, 30) : 'Anonymous',
    time,
    difficulty,
    hints,
  };
  const scores = [...getLeaderboard(), score]
    .sort((first, second) => first.time - second.time)
    .slice(0, MAX_LEADERBOARD_ENTRIES);
  try {
    localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(scores));
  } catch (error) {
    // Private browsing and disabled storage should not interrupt completion.
  }
  renderLeaderboard();
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function readBoard() {
  const inputs = document.querySelectorAll('#sudoku-board input');
  const board = Array.from({length: SIZE}, () => Array(SIZE).fill(0));
  inputs.forEach((input) => {
    const value = input.value;
    board[Number(input.dataset.row)][Number(input.dataset.col)] = value ? parseInt(value, 10) : 0;
  });
  return board;
}

function hasRuleConflict(board, row, col) {
  const value = board[row][col];
  if (!value) return false;

  for (let index = 0; index < SIZE; index++) {
    if (index !== col && board[row][index] === value) return true;
    if (index !== row && board[index][col] === value) return true;
  }

  const boxRow = Math.floor(row / 3) * 3;
  const boxCol = Math.floor(col / 3) * 3;
  for (let boxRowIndex = boxRow; boxRowIndex < boxRow + 3; boxRowIndex++) {
    for (let boxColIndex = boxCol; boxColIndex < boxCol + 3; boxColIndex++) {
      if ((boxRowIndex !== row || boxColIndex !== col) && board[boxRowIndex][boxColIndex] === value) {
        return true;
      }
    }
  }
  return false;
}

function setCellFeedback(input, feedback) {
  input.classList.remove('incorrect', 'conflict');
  if (feedback) input.classList.add(feedback);
}

function setMessage(text, color = '#d32f2f') {
  const message = document.getElementById('message');
  message.innerText = text;
  message.style.color = color === '#388e3c' ? 'var(--success)' : 'var(--error)';
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
  const seconds = (totalSeconds % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function updateTimer() {
  const elapsedSeconds = Math.floor((Date.now() - gameStartedAt) / 1000);
  document.getElementById('timer').innerText = `Time: ${formatTime(elapsedSeconds)}`;
}

function startTimer() {
  clearInterval(timerInterval);
  gameStartedAt = Date.now();
  updateTimer();
  timerInterval = setInterval(updateTimer, 1000);
}

function isSolved(board, incorrect) {
  const allCellsFilled = board.every((row) => row.every((value) => value !== 0));
  return allCellsFilled && incorrect.length === 0;
}

function isBoardFilled(board) {
  return board.every((row) => row.every((value) => value !== 0));
}

function showCompletion(board, incorrect, completedSeconds = null) {
  if (gameCompleted || !isSolved(board, incorrect)) return;

  gameCompleted = true;
  clearInterval(timerInterval);
  const elapsedSeconds = completedSeconds ?? Math.floor((Date.now() - gameStartedAt) / 1000);
  document.getElementById('timer').innerText = `Time: ${formatTime(elapsedSeconds)}`;
  const hintsUsed = document.getElementById('hints-used').innerText.split(': ')[1];
  addLeaderboardScore(elapsedSeconds, document.getElementById('difficulty').value, Number(hintsUsed) || 0);
  document.querySelectorAll('#sudoku-board input').forEach((input) => {
    if (!input.classList.contains('prefilled')) input.disabled = true;
  });
  setMessage(`Congratulations! You solved it in ${formatTime(elapsedSeconds)} with ${hintsUsed} hints.`, '#388e3c');
}

async function validateCell(input) {
  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  const board = readBoard();
  if (hasRuleConflict(board, row, col)) {
    setCellFeedback(input, 'conflict');
    setMessage('This value conflicts with another number in its row, column, or box.');
    return;
  }

  setCellFeedback(input, '');
  if (!board[row][col]) return;

  const response = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await response.json();
  if (data.error) {
    setMessage(data.error);
    return;
  }
  const isIncorrect = data.incorrect.some((position) => position[0] === row && position[1] === col);
  setCellFeedback(input, isIncorrect ? 'incorrect' : '');
  setMessage(isIncorrect ? 'That value does not match the solution.' : '');
  if (JSON.stringify(readBoard()) === JSON.stringify(board)) {
    showCompletion(board, data.incorrect, data.elapsed_seconds);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  gameCompleted = false;
  startTimer();
  document.getElementById('hints-used').innerText = 'Hints used: 0';
  setMessage('');
}

async function useHint() {
  const response = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: readBoard()})
  });
  const data = await response.json();
  if (data.error) {
    setMessage(data.error);
    return;
  }

  const inputs = document.querySelectorAll('#sudoku-board input');
  const input = inputs[data.row * SIZE + data.col];
  input.value = data.value;
  input.disabled = true;
  input.classList.add('hinted');
  document.getElementById('hints-used').innerText = `Hints used: ${data.hints_used}`;
  setMessage('A correct value was added.', '#388e3c');
  if (isBoardFilled(readBoard())) checkSolution();
}

async function checkSolution() {
  const inputs = document.querySelectorAll('#sudoku-board input');
  const board = readBoard();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = 'var(--error)';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.classList.remove('incorrect', 'conflict');
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
    }
  }
  if (isSolved(board, data.incorrect)) {
    showCompletion(board, data.incorrect, data.elapsed_seconds);
  } else if (!isBoardFilled(board) && incorrect.size === 0) {
    msg.style.color = 'var(--error)';
    msg.innerText = 'Fill in all cells to complete the puzzle.';
  } else {
    msg.style.color = 'var(--error)';
    msg.innerText = 'Some cells are incorrect.';
  }
}

function handleBoardInput(event) {
  if (event.target.matches('input.sudoku-cell:not(:disabled)')) {
    event.target.value = event.target.value.replace(/[^1-9]/g, '');
    validateCell(event.target);
  }
}

function handleControlClick(event) {
  const action = event.target.closest('[data-action]')?.dataset.action;
  if (action === 'new-game') newGame();
  if (action === 'check-puzzle') checkSolution();
  if (action === 'hint') useHint();
}

window.addEventListener('load', () => {
  let savedTheme = 'light';
  try {
    savedTheme = localStorage.getItem(THEME_STORAGE_KEY) === 'dark' ? 'dark' : 'light';
  } catch (error) {
    // Use the light theme when storage is unavailable.
  }
  applyTheme(savedTheme);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('sudoku-board').addEventListener('input', handleBoardInput);
  document.querySelector('.controls').addEventListener('click', handleControlClick);
  document.getElementById('difficulty').addEventListener('change', newGame);
  renderLeaderboard();
  newGame();
});