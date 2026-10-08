"""Flask API and dashboard entry point."""
from flask import Flask, jsonify, render_template, request
from database import database, initialize_database
from config import DATABASE_PATH

def create_app(db_path=DATABASE_PATH):
    app = Flask(__name__)
    initialize_database(db_path)

    @app.get("/")
    def index(): return render_template("index.html")

    @app.get("/api/stats")
    def stats():
        with database(db_path) as db:
            result = db.execute("""SELECT (SELECT COUNT(*) FROM events) total_events,
              (SELECT COUNT(*) FROM alerts) total_alerts,
              (SELECT COUNT(*) FROM alerts WHERE severity='High') high_severity,
              (SELECT COUNT(*) FROM alerts WHERE severity='Medium') medium_severity,
              (SELECT COUNT(*) FROM alerts WHERE severity='Low') low_severity,
              (SELECT COUNT(DISTINCT source_ip) FROM events) unique_ips""").fetchone()
        return jsonify(dict(result))

    @app.get("/api/events")
    def events():
        limit = _limit(request.args.get("limit"))
        if limit is None: return jsonify({"error": "limit must be a whole number"}), 400
        with database(db_path) as db:
            rows = db.execute("SELECT id,timestamp,source_ip,username,event_type,status,resource,message FROM events ORDER BY timestamp DESC,id DESC LIMIT ?", (limit,)).fetchall()
        return jsonify([dict(row) for row in rows])

    @app.get("/api/alerts")
    def alerts():
        severity = request.args.get("severity")
        if severity and severity not in ("Low", "Medium", "High"):
            return jsonify({"error": "severity must be Low, Medium, or High"}), 400
        limit = _limit(request.args.get("limit"))
        if limit is None: return jsonify({"error": "limit must be a whole number"}), 400
        query = "SELECT id,event_id,timestamp,source_ip,alert_type,severity,description,status FROM alerts"
        params = []
        if severity: query += " WHERE severity=?"; params.append(severity)
        query += " ORDER BY timestamp DESC,id DESC LIMIT ?"; params.append(limit)
        with database(db_path) as db: rows = db.execute(query, params).fetchall()
        return jsonify([dict(row) for row in rows])

    @app.get("/api/top-ips")
    def top_ips():
        with database(db_path) as db:
            rows = db.execute("SELECT source_ip,COUNT(*) event_count FROM events GROUP BY source_ip ORDER BY event_count DESC,source_ip LIMIT 10").fetchall()
        return jsonify([dict(row) for row in rows])

    @app.get("/api/timeline")
    def timeline():
        with database(db_path) as db:
            rows = db.execute("""SELECT substr(timestamp,1,10) date, COUNT(*) event_count,
               (SELECT COUNT(*) FROM alerts a WHERE substr(a.timestamp,1,10)=substr(e.timestamp,1,10)) alert_count
               FROM events e GROUP BY date ORDER BY date""").fetchall()
        return jsonify([dict(row) for row in rows])

    return app

def _limit(value):
    if value is None: return 100
    try: limit = int(value)
    except ValueError: return None
    return max(1, min(limit, 500))

app = create_app()
if __name__ == "__main__": app.run(debug=False)
