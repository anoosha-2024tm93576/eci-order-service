import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"

def test_create_order_requires_idempotency():
    payload = {
        "customer_id": 1,
        "items": [
            {"product_id": 1, "sku": "T-1", "name": "Test", "quantity": 1, "unit_price": 10.0}
        ],
        "shipping": 0
    }
    r = client.post("/v1/orders", json=payload)
    assert r.status_code == 400