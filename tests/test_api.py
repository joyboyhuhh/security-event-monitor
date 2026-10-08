from app import create_app

def test_api_basics_and_validation(tmp_path):
    client=create_app(tmp_path/"api.db").test_client()
    stats=client.get("/api/stats");assert stats.status_code==200 and stats.json["total_events"]==0
    assert client.get("/api/events?limit=5").json==[]
    assert client.get("/api/events?limit=oops").status_code==400
    assert client.get("/api/alerts?severity=bad").status_code==400
    assert client.get("/").status_code==200
