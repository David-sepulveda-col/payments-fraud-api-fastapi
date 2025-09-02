
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def auth_token():
    client.post("/auth/register", json={"email":"demo@test.com","password":"123456"})
    r = client.post("/auth/login", json={"email":"demo@test.com","password":"123456"})
    return r.json()["access_token"]

def test_order_and_score():
    token = auth_token()
    # crear orden
    r = client.post("/orders", headers={"Authorization": f"Bearer {token}"}, json={
        "customer_id":"cust_X",
        "items":[{"sku":"SKU1","qty":1,"unit_price":350.0}],
        "shipping_address":"CL 1 #2-3"
    })
    assert r.status_code == 200
    order_id = r.json()["id"]
    # score fraude
    r = client.post("/fraud/score", headers={"Authorization": f"Bearer {token}"}, json={
        "order_id": order_id, "ip_country":"RU","email_domain":"yopmail.com","distance_km":2000,
        "attempts_last_hour":3,"ticket_amount":350.0
    })
    assert r.status_code == 200
    data = r.json()
    assert "score" in data and "decision" in data
