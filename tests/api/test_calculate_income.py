import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_calculate_income_ok():
    payload = {
        "name": "A",
        "lo": 300,
        "team": [
            {"name": "B", "lo": 200, "team": []}
        ],
    }

    response = client.post("/mlm/calculate", json=payload)

    assert response.status_code == 200

    data = response.json()


    assert data["error"] == False
    assert data["data"]["name"] == "A"
    assert data["data"]["go"] == 500
    assert "error_msg" in data


@pytest.mark.parametrize(
    "payload, expected_error, expected_message",
    [
        (
            {"name": "A", "lo": -100, "team": []},
            True,
            "Invalid payload: LO cannot be negative",
        ),
        (
            {"name": "B", "lo": -1, "team": []},
            True,
            "Invalid payload: LO cannot be negative",
        ),
    ],
)
def test_api_returns_domain_error(payload, expected_error, expected_message):

    response = client.post("/mlm/calculate", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["error"] == expected_error
    assert data["error_msg"] == expected_message
