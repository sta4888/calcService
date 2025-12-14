from app.domain.models.member import Member
from app.domain.services.income_calculator import IncomeCalculator


def test_personal_bonus_only():
    """
    Один участник, без структуры
    """
    member = Member(name="A", lo=200)
    calc = IncomeCalculator()

    result = calc.calculate(member)

    assert result.lo == 200
    assert result.go == 200
    assert result.level == 0.06
    assert result.personal_bonus == 200 * 0.06
    assert result.structure_bonus == 0
    assert result.total_income == 200 * 0.06


def test_simple_structure_bonus():
    """
    A (400) -> B (200)
    """
    root = Member(
        name="A",
        lo=400,
        team=[Member("B", 200)],
    )

    calc = IncomeCalculator()
    result = calc.calculate(root)

    # уровни
    # A: GO=600 -> 0.09
    # B: GO=200 -> 0.06
    # diff = 0.03

    expected_structure_bonus = 200 * 0.03

    assert result.structure_bonus == expected_structure_bonus


def test_deep_structure_bonus():
    """
    A (300)
      └─ B (500)
          └─ C (400)
    """
    root = Member(
        name="A",
        lo=300,
        team=[
            Member(
                "B",
                500,
                team=[Member("C", 400)],
            )
        ],
    )

    calc = IncomeCalculator()
    result = calc.calculate(root)

    # Проверяем, что бонус не отрицательный
    assert result.structure_bonus >= 0
    assert result.total_income > result.personal_bonus
