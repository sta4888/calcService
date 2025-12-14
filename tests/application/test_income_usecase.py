from application.calculate_income import IncomeCalculatorUseCase


def test_use_case_builds_structure():
    data = {
        "name": "A",
        "lo": 300,
        "team": [
            {
                "name": "B",
                "lo": 200,
                "team": [],
            }
        ],
    }

    use_case = IncomeCalculatorUseCase()
    result = use_case.execute(data)

    assert result.name == "A"
    assert result.go == 500
    # assert "total_income" in result
