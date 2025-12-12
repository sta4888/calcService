from app.domain.models.member import Member
from app.domain.services.mlm_calculator import calc_income

class IncomeCalculatorUseCase:
    def execute(self, data: dict) -> dict:
        """
        data — dict из API, но без FastAPI моделей
        """
        root = self._create_member_tree(data)
        return calc_income(root)

    def _create_member_tree(self, node):
        team = [
            self._create_member_tree(child)
            for child in node.get("team", [])
        ]
        return Member(
            name=node["name"],
            lo=node["lo"],
            team=team
        )
