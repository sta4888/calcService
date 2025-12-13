from app.domain.models.member import Member
from app.domain.services.mlm_calculator import calc_income
from typing import Dict, Any


class IncomeCalculatorUseCase:
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data:
            return {}  # пустой вход

        try:
            root = self._create_member_tree(data)
            result = calc_income(root)

            # если calc_income вернул None или не dict
            if not isinstance(result, dict):
                return {}

            return result

        except Exception as e:
            print(f"IncomeCalculatorUseCase error: {e}")
            return {}

    def _create_member_tree(self, node: Dict[str, Any]) -> Member:
        if not node:
            return Member(name="Unknown", lo=0, team=[])

        team_data = node.get("team") or []
        team = [self._create_member_tree(child) for child in team_data]

        name = node.get("name", "Unknown")
        lo = node.get("lo", 0)

        return Member(name=name, lo=lo, team=team)
