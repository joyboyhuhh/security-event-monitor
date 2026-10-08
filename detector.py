"""Small, explainable rules for the fictional security-event dataset."""
import hashlib
from datetime import timedelta
from database import database, initialize_database
from config import DATABASE_PATH

def run_detection(db_path=DATABASE_PATH):
    initialize_database(db_path)
    created = 0
    with database(db_path) as connection:
        events = [dict(row) for row in connection.execute("SELECT * FROM events ORDER BY timestamp, id")]
        candidates = []
        failures = [e for e in events if e["event_type"].lower() in ("login", "failed login") and e["status"].lower() in ("failed", "failure", "denied")]
        for event in failures:
            start = event["timestamp"]
            end = (pd_timestamp(start) + timedelta(minutes=10)).isoformat()
            count = sum(1 for item in failures if item["source_ip"] == event["source_ip"] and start <= item["timestamp"] <= end)
            if count >= 5:
                candidates.append((event, "Brute Force", "High", "Five or more failed login attempts from this IP within 10 minutes."))
            elif count >= 3:
                candidates.append((event, "Repeated Failed Login", "Medium", "Three or more failed login attempts from this IP within 10 minutes."))
        for event in events:
            kind = (event["event_type"] + " " + event["resource"] + " " + event["message"]).lower()
            if "restricted" in kind or "admin" in event["resource"].lower():
                candidates.append((event, "Restricted Resource Access", "Medium", "An event referenced a restricted or admin resource."))
            if "privilege escalation" in kind or "privilege escalation" in event["event_type"].lower():
                candidates.append((event, "Privilege Escalation", "High", "A privilege escalation attempt was recorded."))
            if any(pattern in kind for pattern in ("../", "<script", "union select")):
                candidates.append((event, "Suspicious Request", "High", "A fictional request contains a suspicious input pattern."))
        for event, alert_type, severity, description in candidates:
            fingerprint = hashlib.sha256(f"{event['id']}|{alert_type}".encode()).hexdigest()
            cursor = connection.execute("""INSERT OR IGNORE INTO alerts
              (event_id,timestamp,source_ip,alert_type,severity,description,fingerprint)
              VALUES (?,?,?,?,?,?,?)""", (event["id"],event["timestamp"],event["source_ip"],alert_type,severity,description,fingerprint))
            created += cursor.rowcount
    return created

def pd_timestamp(value):
    from datetime import datetime
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

if __name__ == "__main__": print(f"Created {run_detection()} new alerts.")
