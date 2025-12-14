from tests.api.test_calculate_income import client


def test_validation_error():
    payload = {
        "name": "A",
        # lo отсутствует
        "team": [],
    }

    response = client.post("/mlm/calculate", json=payload)

    assert response.status_code == 422
