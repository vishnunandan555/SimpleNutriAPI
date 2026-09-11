import os
import sys
from pathlib import Path

# Add project root directory to sys.path so backend imports work seamlessly
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Mark environment as Vercel
os.environ["VERCEL"] = "1"

from backend.app.main import app
