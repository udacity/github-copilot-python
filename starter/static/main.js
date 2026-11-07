// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const MAX_SCOREBOARD_ENTRIES = 10;
let puzzle = [];
let lockedCells = [];
let hintsUsed = 0;
let elapsedTime = 0;
let timerInterval = null;
let currentCompletionStats = null;
let activeHighlightTimeout = null;
let previousHighlightStates = new Map();

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const timerDisplay = document.getElementById('timer-display');
  if (timerDisplay) {
    timerDisplay.innerText = `Time: ${formatTime(elapsedTime)}`;
  }
}

function setTheme(theme) {
  const body = document.body;
  const themeToggle = document.getElementById('theme-toggle');
  const normalizedTheme = theme === 'dark' ? 'dark' : 'light';

  body.setAttribute('data-theme', normalizedTheme);

  if (themeToggle) {
    themeToggle.innerText = normalizedTheme === 'dark' ? 'Light' : 'Dark';
  }

  try {
    localStorage.setItem('sudokuTheme', normalizedTheme);
  } catch (error) {
    console.error('Unable to save theme preference:', error);
  }
}

function toggleTheme() {
  const currentTheme = document.body.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  setTheme(currentTheme === 'dark' ? 'light' : 'dark');
}

function loadSavedTheme() {
  try {
    const savedTheme = localStorage.getItem('sudokuTheme');
    if (savedTheme === 'dark' || savedTheme === 'light') {
      setTheme(savedTheme);
      return;
    }
  } catch (error) {
    console.error('Unable to load theme preference:', error);
  }

  setTheme('light');
}

function focusBoardCell(row, col) {
  if (row < 0 || row >= SIZE || col < 0 || col >= SIZE) {
    return;
  }
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const idx = row * SIZE + col;
  const target = inputs[idx];
  if (isInputEditable(target)) {
    target.focus();
  }
}

function handleCellNavigation(event) {
  const key = event.key;
  const row = parseInt(event.target.dataset.row, 10);
  const col = parseInt(event.target.dataset.col, 10);
  let nextRow = row;
  let nextCol = col;

  if (key === 'ArrowLeft') {
    nextCol = col > 0 ? col - 1 : col;
  } else if (key === 'ArrowRight') {
    nextCol = col < SIZE - 1 ? col + 1 : col;
  } else if (key === 'ArrowUp') {
    nextRow = row > 0 ? row - 1 : row;
  } else if (key === 'ArrowDown') {
    nextRow = row < SIZE - 1 ? row + 1 : row;
  } else if (key === 'Enter') {
    event.preventDefault();
    if (col < SIZE - 1) {
      nextCol = col + 1;
    } else if (row < SIZE - 1) {
      nextRow = row + 1;
      nextCol = 0;
    }
  }

  if (nextRow !== row || nextCol !== col) {
    event.preventDefault();
    focusBoardCell(nextRow, nextCol);
  }
}

function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function startTimer() {
  stopTimer();
  updateTimerDisplay();
  timerInterval = setInterval(() => {
    elapsedTime += 1;
    updateTimerDisplay();
  }, 1000);
}

function getSavedScores() {
  try {
    const stored = localStorage.getItem('sudokuScores');
    const parsed = stored ? JSON.parse(stored) : [];
    if (Array.isArray(parsed)) {
      return parsed.slice(0, MAX_SCOREBOARD_ENTRIES);
    }
    return [];
  } catch (error) {
    console.error('Failed to load scores:', error);
    return [];
  }
}

function saveScores(scores) {
  try {
    const trimmed = Array.isArray(scores) ? scores.slice(0, MAX_SCOREBOARD_ENTRIES) : [];
    localStorage.setItem('sudokuScores', JSON.stringify(trimmed));
  } catch (error) {
    console.error('Failed to save scores:', error);
  }
}

function updateScoreboardDisplay() {
  fetch('/scores')
    .then(res => res.json())
    .then(data => {
      if (data.scores && Array.isArray(data.scores)) {
        saveScores(data.scores);
        displayScoreboardTable(data.scores);
      } else {
        displayScoreboardTable(getSavedScores());
      }
    })
    .catch(error => {
      console.error('Failed to fetch scores from server, using localStorage:', error);
      displayScoreboardTable(getSavedScores());
    });
}

function displayScoreboardTable(scores) {
  const tbody = document.querySelector('#scoreboard-table tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (scores.length === 0) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 5;
    cell.innerText = 'No scores yet';
    row.appendChild(cell);
    tbody.appendChild(row);
    return;
  }

  // Ensure we only render the top N entries
  const displayScores = Array.isArray(scores) ? scores.slice(0, MAX_SCOREBOARD_ENTRIES) : [];

  displayScores.forEach((score, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${score.name}</td>
      <td>${formatTime(score.elapsed_time)}</td>
      <td>${score.difficulty}</td>
      <td>${score.hints_used}</td>
    `;
    tbody.appendChild(row);
  });
}

function validatePlayerName(name) {
  return typeof name === 'string' && name.trim().length >= 1 && name.trim().length <= 30;
}

function displayScoreSaveMessage(text, isError = false) {
  const message = document.getElementById('score-save-message');
  if (!message) return;
  message.innerText = text;
  message.classList.toggle('message-error', isError);
  message.classList.toggle('message-success', !isError && Boolean(text));
}

function setStatusMessage(text, isError = false) {
  const msg = document.getElementById('message');
  if (!msg) return;
  msg.innerText = text;
  msg.classList.toggle('message-error', isError);
  msg.classList.toggle('message-success', !isError && Boolean(text));
}

function saveCurrentScore() {
  const nameInput = document.getElementById('player-name');
  if (!nameInput || !currentCompletionStats) {
    return;
  }

  const playerName = nameInput.value.trim();
  if (!validatePlayerName(playerName)) {
    displayScoreSaveMessage('Name must be 1-30 characters.', true);
    return;
  }

  const scores = getSavedScores();
  scores.push({
    name: playerName,
    elapsed_time: currentCompletionStats.elapsed_time,
    difficulty: currentCompletionStats.difficulty,
    hints_used: currentCompletionStats.hints_used,
    saved_at: new Date().toISOString()
  });

  scores.sort((a, b) => a.elapsed_time - b.elapsed_time);
  saveScores(scores);
  updateScoreboardDisplay();

  // Sync score with server (fire-and-forget)
  const serverScore = {
    name: playerName,
    elapsed_time: currentCompletionStats.elapsed_time,
    difficulty: currentCompletionStats.difficulty,
    hints_used: currentCompletionStats.hints_used,
  };
  fetch('/scores', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(serverScore)
  }).catch(error => console.error('Failed to sync score with server:', error));

  displayScoreSaveMessage('Score saved successfully.');
  document.getElementById('save-score').disabled = true;
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
      input.inputMode = 'numeric';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.setAttribute('role', 'gridcell');
      input.setAttribute('aria-label', `Row ${i + 1}, Column ${j + 1}`);
      input.setAttribute('autocomplete', 'off');
      input.addEventListener('input', (e) => {
        const row = parseInt(e.target.dataset.row, 10);
        const col = parseInt(e.target.dataset.col, 10);
        // Check if this cell is locked
        if (isLockedCell(row, col)) {
          e.target.value = '';
          return;
        }
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        // Validate board after input
        setTimeout(() => validateBoard(), 10);
      });
      input.addEventListener('keydown', handleCellNavigation);
      input.addEventListener('dblclick', (e) => {
        const value = e.target.value;
        if (value && value !== '') {
          highlightCellsWithValue(value);
        }
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function isLockedCell(row, col) {
  return lockedCells.some(cell => cell.row === row && cell.col === col);
}

function isInputEditable(input) {
  return input && !input.disabled && !input.readOnly;
}

function highlightCellsWithValue(value) {
  // Cancel any active highlight timeout
  if (activeHighlightTimeout !== null) {
    clearTimeout(activeHighlightTimeout);
  }
  
  // Clear any previous highlight states
  previousHighlightStates.clear();
  
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  
  // Find all cells with matching value and highlight them
  for (let i = 0; i < inputs.length; i++) {
    const cell = inputs[i];
    if (cell.value === value) {
      // Store the current class state before highlighting
      previousHighlightStates.set(cell, cell.className);
      
      // Remove conflict class temporarily and add highlighted class
      cell.classList.remove('conflict');
      cell.classList.add('highlighted');
    }
  }
  
  // Schedule restoration after 2 seconds
  activeHighlightTimeout = setTimeout(restoreHighlighting, 2000);
}

function restoreHighlighting() {
  // Restore each cell to its previous state
  for (const [cell, previousClassName] of previousHighlightStates.entries()) {
    cell.className = previousClassName;
  }
  
  // Clear the map and timeout
  previousHighlightStates.clear();
  activeHighlightTimeout = null;
}

function renderPuzzle(puz, locked) {
  puzzle = puz;
  lockedCells = locked || [];
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
        inp.readOnly = true;
        inp.disabled = false;
        inp.className = 'sudoku-cell prefilled';
      } else {
        inp.value = '';
        inp.readOnly = false;
        inp.disabled = false;
        inp.className = 'sudoku-cell';
      }
    }
  }
  updateHintButtonState();
}

async function newGame() {
  stopTimer();
  elapsedTime = 0;
  updateTimerDisplay();

  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  if (data.error) {
    setStatusMessage(data.error, true);
    return;
  }
  hintsUsed = 0;
  updateHintCounter();
  renderPuzzle(data.puzzle, data.locked_cells);
  setStatusMessage('');
  startTimer();
}

async function checkSolution() {
  const board = getBoardFromDOM();
  const res = await fetch('/check-complete', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  
  if (data.is_complete) {
    stopTimer();
    currentCompletionStats = {
      elapsed_time: data.elapsed_time,
      difficulty: data.difficulty,
      hints_used: data.hints_used
    };
    // Show congratulations modal with stats
    showCongratsModal(data.elapsed_time, data.difficulty, data.hints_used);
    setStatusMessage(data.message, false);
    updateHintButtonState();
  } else {
    setStatusMessage(data.message, true);
    updateHintButtonState();
  }
}

async function requestHint() {
  try {
    const board = getBoardFromDOM();
    const res = await fetch('/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    const data = await res.json();
    const msg = document.getElementById('message');

    if (data.error) {
      setStatusMessage(data.error, true);
      return;
    }

    const boardDiv = document.getElementById('sudoku-board');
    const inputs = boardDiv.getElementsByTagName('input');
    const idx = data.row * SIZE + data.col;
    const inp = inputs[idx];
    inp.value = data.value;
    // Make the hinted cell readonly (preserve event handling) and ensure it's not disabled
    inp.readOnly = true;
    inp.disabled = false;
    inp.className = 'sudoku-cell prefilled';
    lockedCells.push({row: data.row, col: data.col});
    hintsUsed += 1;
    updateHintCounter();
    updateHintButtonState();
    validateBoard();
    setStatusMessage('Hint applied.', false);
  } catch (error) {
    console.error('Hint request failed:', error);
  }
}

async function checkBoard() {
  const board = getBoardFromDOM();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');

  try {
    const res = await fetch('/validate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    const data = await res.json();
    const msg = document.getElementById('message');

    clearCheckHighlights();

    if (data.conflicts && data.conflicts.length > 0) {
      const invalidPositions = new Set();
      for (const conflict of data.conflicts) {
        if (conflict.positions) {
          for (const pos of conflict.positions) {
            invalidPositions.add(pos.row * SIZE + pos.col);
          }
        }
      }
      for (const idx of invalidPositions) {
        const inp = inputs[idx];
        inp.classList.add('check-highlight');
      }
      setStatusMessage('Incorrect cells highlighted.', true);
      setTimeout(clearCheckHighlights, 2000);
    } else {
      setStatusMessage('No incorrect cells found.', false);
    }
  } catch (error) {
    console.error('Check failed:', error);
  }
}

function clearCheckHighlights() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let idx = 0; idx < inputs.length; idx++) {
    inputs[idx].classList.remove('check-highlight');
  }
}

async function validateBoard() {
  const board = getBoardFromDOM();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  
  try {
    const res = await fetch('/validate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    const data = await res.json();
    
    // Clear all conflict highlights first
    for (let idx = 0; idx < inputs.length; idx++) {
      const inp = inputs[idx];
      inp.classList.remove('conflict');
    }
    
    // Highlight conflicting cells
    if (data.conflicts && data.conflicts.length > 0) {
      const conflictPositions = new Set();
      
      // Collect all positions involved in conflicts
      for (const conflict of data.conflicts) {
        if (conflict.positions) {
          for (const pos of conflict.positions) {
            const idx = pos.row * SIZE + pos.col;
            conflictPositions.add(idx);
          }
        }
      }
      
      // Apply conflict highlighting
      for (const idx of conflictPositions) {
        const inp = inputs[idx];
        if (isInputEditable(inp)) { // Only highlight editable cells
          inp.classList.add('conflict');
        }
      }
    }
  } catch (error) {
    console.error('Validation failed:', error);
  }
}

function updateHintCounter() {
  const hintCountSpan = document.getElementById('hint-count');
  hintCountSpan.innerText = `Hints: ${hintsUsed}`;
}

function hasEmptyCells() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  return Array.from(inputs).some(inp => isInputEditable(inp) && inp.value === '');
}

function getBoardFromDOM() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];

  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }

  return board;
}

function updateHintButtonState() {
  const hintButton = document.getElementById('hint-button');
  hintButton.disabled = !hasEmptyCells();
}

function showCongratsModal(elapsedTime, difficulty, hintsUsed) {
  // Format elapsed time as MM:SS
  const minutes = Math.floor(elapsedTime / 60);
  const seconds = elapsedTime % 60;
  const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;
  
  // Capitalize difficulty
  const diffStr = difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
  
  // Update modal stats
  document.getElementById('stat-time').innerText = timeStr;
  document.getElementById('stat-difficulty').innerText = diffStr;
  document.getElementById('stat-hints').innerText = hintsUsed;

  const nameInput = document.getElementById('player-name');
  const saveButton = document.getElementById('save-score');
  displayScoreSaveMessage('');
  if (nameInput) {
    nameInput.value = '';
  }
  if (saveButton) {
    saveButton.disabled = false;
  }
  
  const modal = document.getElementById('congrats-modal');
  modal.setAttribute('aria-hidden', 'false');
  modal.style.display = 'block';
}

function hideCongratsModal() {
  const modal = document.getElementById('congrats-modal');
  modal.setAttribute('aria-hidden', 'true');
  modal.style.display = 'none';
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('check-board').addEventListener('click', checkBoard);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  document.getElementById('save-score').addEventListener('click', saveCurrentScore);

  const playerNameInput = document.getElementById('player-name');
  if (playerNameInput) {
    playerNameInput.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        saveCurrentScore();
      }
    });
  }
  
  // Modal event handlers
  document.getElementById('play-again').addEventListener('click', () => {
    hideCongratsModal();
    newGame();
  });
  
  document.getElementById('close-modal').addEventListener('click', hideCongratsModal);
  
  // Close modal when clicking outside
  window.addEventListener('click', (event) => {
    const modal = document.getElementById('congrats-modal');
    if (event.target === modal) {
      hideCongratsModal();
    }
  });
  
  // initialize
  loadSavedTheme();
  updateScoreboardDisplay();
  newGame();
});