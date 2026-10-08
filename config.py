"""Project paths and settings."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = BASE_DIR / "security_events.db"
SAMPLE_LOG_PATH = DATA_DIR / "security_logs.csv"
REQUIRED_COLUMNS = ["timestamp", "source_ip", "username", "event_type", "status", "resource", "message"]
