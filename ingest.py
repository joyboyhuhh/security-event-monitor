"""Validate fictional CSV events and load valid rows into SQLite."""
import hashlib
import ipaddress
import sqlite3
import pandas as pd
from config import REQUIRED_COLUMNS, SAMPLE_LOG_PATH
from database import database, initialize_database

class LogFileError(ValueError):
    """An input file cannot be read or does not have the expected shape."""

def _clean(value):
    return "" if pd.isna(value) else str(value).strip()

def parse_logs(csv_path=SAMPLE_LOG_PATH):
    try:
        frame = pd.read_csv(csv_path)
    except FileNotFoundError as exc:
        raise LogFileError(f"CSV file not found: {csv_path}") from exc
    except pd.errors.EmptyDataError as exc:
        raise LogFileError(f"CSV file is empty: {csv_path}") from exc
    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise LogFileError(f"Could not parse CSV file: {exc}") from exc
    missing = [name for name in REQUIRED_COLUMNS if name not in frame.columns]
    if missing:
        raise LogFileError("Missing required columns: " + ", ".join(missing))
    valid, invalid = [], []
    for line_number, row in enumerate(frame[REQUIRED_COLUMNS].to_dict("records"), start=2):
        item = {key: _clean(value) for key, value in row.items()}
        reasons = []
        try:
            item["timestamp"] = pd.to_datetime(item["timestamp"], utc=True, errors="raise").isoformat()
        except (ValueError, TypeError):
            reasons.append("invalid timestamp")
        try:
            item["source_ip"] = str(ipaddress.ip_address(item["source_ip"]))
        except ValueError:
            reasons.append("invalid IP address")
        for field in ("username", "event_type", "status"):
            if not item[field]: reasons.append(f"missing {field}")
        if reasons:
            invalid.append({"line": line_number, "reasons": reasons})
        else:
            item["fingerprint"] = hashlib.sha256("|".join(item[key] for key in REQUIRED_COLUMNS).encode()).hexdigest()
            valid.append(item)
    return valid, invalid

def ingest_logs(csv_path=SAMPLE_LOG_PATH, db_path=None):
    from config import DATABASE_PATH
    target = db_path or DATABASE_PATH
    initialize_database(target)
    rows, invalid = parse_logs(csv_path)
    inserted = 0
    with database(target) as connection:
        for row in rows:
            cursor = connection.execute("""INSERT OR IGNORE INTO events
              (timestamp,source_ip,username,event_type,status,resource,message,fingerprint)
              VALUES (:timestamp,:source_ip,:username,:event_type,:status,:resource,:message,:fingerprint)""", row)
            inserted += cursor.rowcount
    return {"read": len(rows) + len(invalid), "inserted": inserted, "duplicates": len(rows)-inserted, "invalid": invalid}

if __name__ == "__main__":
    try:
        result = ingest_logs()
        print(f"Read {result['read']} rows; imported {result['inserted']}; duplicates {result['duplicates']}; skipped {len(result['invalid'])}.")
        for issue in result["invalid"]: print(f"Warning: CSV line {issue['line']} skipped: {', '.join(issue['reasons'])}")
    except LogFileError as exc:
        raise SystemExit(str(exc))
