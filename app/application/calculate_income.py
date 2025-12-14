from app.domain.models.member import Member
from app.domain.services.income_calculator import IncomeCalculator


class IncomeCalculatorUseCase:
    def __init__(self):
        self.calculator = IncomeCalculator()

    def execute(self, data: dict):
        root = self._build_member(data)
        return self.calculator.calculate(root)

    def _build_member(self, data: dict) -> Member:
        return Member(
            name=data["name"],
            lo=data["lo"],
            team=[self._build_member(m) for m in data.get("team", [])],
        )
