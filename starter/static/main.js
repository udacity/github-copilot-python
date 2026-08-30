
const SIZE = 9;
const STORAGE_KEY = 'sudoku-top-scores';
let puzzle = [];
let currentSolution = [];
let timerInterval = null;
let startTime = 0;
let hintsUsed = 0;
let gameCompleted = false;

function getMessageElement() {
  return document.getElementById('message');
}

function setMessage(text, isSuccess = false) {
  const msg = getMessageElement();
  msg.innerText = text;
  msg.style.color = isSuccess ? '#2e7d32' : '#d32f2f';
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateTimer() {
  if (!startTime) {
    document.getElementById('timer').textContent = '00:00';
    return;
  }

  const elapsed = Math.floor((Date.now() - startTime) / 1000);
  document.getElementById('timer').textContent = formatTime(elapsed);
}

function startTimer() {
  clearInterval(timerInterval);
  startTime = Date.now();
  updateTimer();
  timerInterval = setInterval(updateTimer, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
}

function getScoreEntries() {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    return Array.isArray(stored) ? stored : [];
  } catch (error) {
    return [];
  }
}

function renderScoreboard() {
  const list = document.getElementById('scoreboard');
  const entries = getScoreEntries().slice(0, 10);

  list.innerHTML = '';
  if (!entries.length) {
    const emptyItem = document.createElement('li');
    emptyItem.className = 'empty';
    emptyItem.textContent = 'No scores yet';
    list.appendChild(emptyItem);
    return;
  }

  entries.forEach((entry, index) => {
    const item = document.createElement('li');
    item.textContent = `${index + 1}. ${entry.name} ? ${formatTime(entry.time)} ? ${entry.difficulty} ? ${entry.hints} hint${entry.hints === 1 ? '' : 's'}`;
    list.appendChild(item);
  });
}

function markScore(name, elapsedSeconds, difficultyLevel, hintCount) {
  const entries = getScoreEntries();
  entries.push({
    name,
    time: elapsedSeconds,
    difficulty: difficultyLevel,
    hints: hintCount,
  });

  entries.sort((a, b) => a.time - b.time || a.hints - b.hints);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries.slice(0, 10)));
  renderScoreboard();
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';

  for (let row = 0; row < SIZE; row += 1) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';

    for (let col = 0; col < SIZE; col += 1) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = String(row);
      input.dataset.col = String(col);

      if ((Math.floor(row / 3) + Math.floor(col / 3)) % 2 === 0) {
        input.classList.add('block-light');
      } else {
        input.classList.add('block-dark');
      }

      if ((col + 1) % 3 === 0 && col !== SIZE - 1) {
        input.style.borderRightWidth = '3px';
      }
      if ((row + 1) % 3 === 0 && row !== SIZE - 1) {
        input.style.borderBottomWidth = '3px';
      }

      input.addEventListener('input', (event) => {
        const target = event.target;
        const value = target.value.replace(/[^1-9]/g, '').slice(0, 1);
        target.value = value;
        updateBoardFeedback();
      });

      rowDiv.appendChild(input);
    }

    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz, solution = []) {
  puzzle = puz;
  currentSolution = solution;
  hintsUsed = 0;
  gameCompleted = false;
  createBoardElement();

  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');

  for (let row = 0; row < SIZE; row += 1) {
    for (let col = 0; col < SIZE; col += 1) {
      const idx = row * SIZE + col;
      const val = puzzle[row][col];
      const input = inputs[idx];
      const cellClassNames = ['sudoku-cell'];

      if ((Math.floor(row / 3) + Math.floor(col / 3)) % 2 === 0) {
        cellClassNames.push('block-light');
      } else {
        cellClassNames.push('block-dark');
      }

      input.className = cellClassNames.join(' ');
      input.classList.remove('prefilled', 'hinted', 'incorrect');

      if ((col + 1) % 3 === 0 && col !== SIZE - 1) {
        input.style.borderRightWidth = '3px';
      } else {
        input.style.borderRightWidth = '1px';
      }

      if ((row + 1) % 3 === 0 && row !== SIZE - 1) {
        input.style.borderBottomWidth = '3px';
      } else {
        input.style.borderBottomWidth = '1px';
      }

      if (val !== 0) {
        input.value = String(val);
        input.disabled = true;
        input.readOnly = true;
        input.classList.add('prefilled');
      } else {
        input.value = '';
        input.disabled = false;
        input.readOnly = false;
      }
    }
  }

  startTimer();
  updateBoardFeedback();
}

function getBoardFromInputs() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];

  for (let row = 0; row < SIZE; row += 1) {
    board[row] = [];
    for (let col = 0; col < SIZE; col += 1) {
      const idx = row * SIZE + col;
      const value = inputs[idx].value;
      board[row][col] = value ? Number.parseInt(value, 10) : 0;
    }
  }

  return board;
}

function boardIsSolved(board) {
  if (!currentSolution || !currentSolution.length) {
    return false;
  }

  for (let row = 0; row < SIZE; row += 1) {
    for (let col = 0; col < SIZE; col += 1) {
      if (board[row][col] !== currentSolution[row][col]) {
        return false;
      }
    }
  }

  return true;
}

function updateBoardFeedback() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = getBoardFromInputs();
  const invalidCells = new Set();

  for (let idx = 0; idx < inputs.length; idx += 1) {
    const input = inputs[idx];
    const row = Number(input.dataset.row);
    const col = Number(input.dataset.col);

    if (input.disabled) {
      input.classList.remove('incorrect');
      continue;
    }

    const value = board[row][col];
    const isIncorrect = value !== 0 && currentSolution[row]?.[col] !== undefined && value !== currentSolution[row][col];
    if (isIncorrect) {
      invalidCells.add(`${row}-${col}`);
    }
    input.classList.toggle('incorrect', isIncorrect);
  }

  if (boardIsSolved(board)) {
    if (!gameCompleted) {
      completeGame();
    }
    return;
  }

  if (invalidCells.size > 0) {
    setMessage('Some entries are incorrect.');
    return;
  }

  setMessage('');
}

function completeGame() {
  gameCompleted = true;
  stopTimer();

  const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
  const difficultyLevel = document.getElementById('difficulty').value;
  const scoreText = `Congratulations! Puzzle complete in ${formatTime(elapsedSeconds)} with ${hintsUsed} hint${hintsUsed === 1 ? '' : 's'}.`;
  setMessage(scoreText, true);

  const playerName = window.prompt('Enter your name for the Top 10 leaderboard:', 'Player');
  const trimmedName = (playerName || '').trim();

  if (trimmedName) {
    markScore(trimmedName, elapsedSeconds, difficultyLevel, hintsUsed);
  }
}

function fillHint() {
  if (gameCompleted) {
    return;
  }

  const board = getBoardFromInputs();
  let targetCell = null;

  for (let row = 0; row < SIZE; row += 1) {
    for (let col = 0; col < SIZE; col += 1) {
      if (board[row][col] === 0 && puzzle[row][col] === 0) {
        targetCell = { row, col };
        break;
      }
    }
    if (targetCell) {
      break;
    }
  }

  if (!targetCell) {
    setMessage('No hint available for this puzzle.');
    return;
  }

  const { row, col } = targetCell;
  const targetInput = document.querySelector(`input[data-row="${row}"][data-col="${col}"]`);
  if (!targetInput) {
    return;
  }

  targetInput.value = String(currentSolution[row][col]);
  targetInput.disabled = true;
  targetInput.readOnly = true;
  targetInput.classList.add('prefilled', 'hinted');
  hintsUsed += 1;
  setMessage(`Hint used: row ${row + 1}, column ${col + 1}.`, false);
  updateBoardFeedback();
}

async function checkBoard() {
  const board = getBoardFromInputs();
  try {
    const res = await fetch('/check', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ board }),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({ error: 'Unable to check puzzle' }));
      setMessage(data.error || 'Unable to check puzzle');
      return;
    }

    const data = await res.json();
    const incorrect = data.incorrect || [];
    const incorrectSet = new Set(incorrect.map(([row, col]) => `${row}-${col}`));

    const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
    for (let idx = 0; idx < inputs.length; idx += 1) {
      const input = inputs[idx];
      if (input.disabled) {
        continue;
      }
      const row = Number(input.dataset.row);
      const col = Number(input.dataset.col);
      input.classList.toggle('incorrect', incorrectSet.has(`${row}-${col}`));
    }

    if (incorrect.length) {
      setMessage('Some entries are incorrect.');
      return;
    }

    if (boardIsSolved(board)) {
      completeGame();
      return;
    }

    setMessage('No incorrect entries found.');
  } catch (error) {
    setMessage('Unable to check puzzle');
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);

  if (!res.ok) {
    const data = await res.json().catch(() => ({ error: 'Unable to load puzzle' }));
    setMessage(data.error || 'Unable to load puzzle');
    return;
  }

  const data = await res.json();
  renderPuzzle(data.puzzle, data.solution || []);
  setMessage('');
}

function toggleDarkMode() {
  const root = document.body;
  const isDark = root.classList.toggle('dark-mode');
  const button = document.getElementById('theme-toggle');
  button.textContent = isDark ? 'Light' : 'Dark';
  localStorage.setItem('sudoku-theme', isDark ? 'dark' : 'light');
}

function applySavedTheme() {
  const preferredTheme = localStorage.getItem('sudoku-theme');
  const isDark = preferredTheme === 'dark';
  document.body.classList.toggle('dark-mode', isDark);
  const button = document.getElementById('theme-toggle');
  if (button) {
    button.textContent = isDark ? 'Light' : 'Dark';
  }
}

window.addEventListener('load', () => {
  applySavedTheme();
  renderScoreboard();

  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('difficulty').addEventListener('change', newGame);
  document.getElementById('hint-button').addEventListener('click', fillHint);
  document.getElementById('check-button').addEventListener('click', checkBoard);
  document.getElementById('theme-toggle').addEventListener('click', toggleDarkMode);

  newGame();
});
