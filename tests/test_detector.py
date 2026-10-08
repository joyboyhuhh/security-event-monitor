from datetime import datetime, timedelta, timezone
from database import initialize_database, database
from detector import run_detection

def add_event(db, when, ip, kind, status, resource="/home", message=""):
    with database(db) as conn:
        conn.execute("INSERT INTO events(timestamp,source_ip,username,event_type,status,resource,message,fingerprint) VALUES(?,?,?,?,?,?,?,?)",(when,ip,"demo",kind,status,resource,message,f"{when}-{kind}-{resource}"))

def test_brute_force_and_duplicate_prevention(tmp_path):
    db=tmp_path/"test.db";initialize_database(db);base=datetime(2026,9,10,tzinfo=timezone.utc)
    for i in range(5):add_event(db,(base+timedelta(minutes=i)).isoformat(),"192.0.2.20","login","failed")
    assert run_detection(db)>0
    with database(db) as conn: before=conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    assert run_detection(db)==0
    with database(db) as conn: assert conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]==before

def test_restricted_and_privilege_escalation(tmp_path):
    db=tmp_path/"test.db";initialize_database(db);now=datetime(2026,9,10,tzinfo=timezone.utc).isoformat()
    add_event(db,now,"192.0.2.21","resource access","success","/admin/settings")
    add_event(db,(datetime.fromisoformat(now)+timedelta(minutes=1)).isoformat(),"192.0.2.22","privilege escalation attempt","blocked")
    run_detection(db)
    with database(db) as conn: types={r[0] for r in conn.execute("SELECT alert_type FROM alerts")}
    assert "Restricted Resource Access" in types and "Privilege Escalation" in types
