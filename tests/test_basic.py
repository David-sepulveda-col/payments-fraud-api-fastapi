
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_register_login():
    # register
    r = client.post("/auth/register", json={"email":"demo@test.com","password":"123456"})
    assert r.status_code in (200, 400)  # puede existir ya si corre 2 veces
    # login
    r = client.post("/auth/login", json={"email":"demo@test.com","password":"123456"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token
