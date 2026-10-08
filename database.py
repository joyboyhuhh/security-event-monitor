"""SQLite setup and small, parameterized data access helpers."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from config import DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
 id INTEGER PRIMARY KEY, timestamp TEXT NOT NULL, source_ip TEXT NOT NULL,
 username TEXT NOT NULL, event_type TEXT NOT NULL, status TEXT NOT NULL,
 resource TEXT NOT NULL, message TEXT NOT NULL, fingerprint TEXT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_events_time ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_ip ON events(source_ip);
CREATE TABLE IF NOT EXISTS alerts (
 id INTEGER PRIMARY KEY, event_id INTEGER NOT NULL REFERENCES events(id),
 timestamp TEXT NOT NULL, source_ip TEXT NOT NULL, alert_type TEXT NOT NULL,
 severity TEXT NOT NULL CHECK(severity IN ('Low','Medium','High')),
 description TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Open',
 fingerprint TEXT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_time ON alerts(timestamp);
"""

def connect(db_path=DATABASE_PATH):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize_database(db_path=DATABASE_PATH):
    with connect(db_path) as connection:
        connection.executescript(SCHEMA)

@contextmanager
def database(db_path=DATABASE_PATH):
    connection = connect(db_path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
