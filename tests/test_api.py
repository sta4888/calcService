from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_mlm_calculate():
    payload = {
        "name": "Root",
        "lo": 300,
        "team": [
            {"name": "A", "lo": 200},
            {"name": "B", "lo": 400}
        ]
    }
    response = client.post("/mlm/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ГО"] == 900
