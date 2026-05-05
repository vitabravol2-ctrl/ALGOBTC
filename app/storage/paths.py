from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

CONFIG_PATH = DATA_DIR / "config.json"
ALGORITHMS_PATH = DATA_DIR / "algorithms.json"
ERROR_LOG_PATH = LOGS_DIR / "errors.log"


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
