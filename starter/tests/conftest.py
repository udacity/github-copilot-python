import sys
from pathlib import Path

# Add parent directory (starter/) to sys.path so tests can import app and sudoku_logic
STARTER_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(STARTER_DIR))