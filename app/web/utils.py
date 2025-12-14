from domain.models.member import Member
from typing import Dict, Any, List


def build_member_from_payload(data: Dict[str, Any]) -> Member:
    """
    Рекурсивно строит объект Member из словаря.
    data: {
        "name": "A",
        "lo": 100,
        "team": [
            {"name": "B", "lo": 50, "team": []}
        ]
    }
    """
    name = data.get("name")
    lo = data.get("lo", 0)
    team_data = data.get("team", [])

    # Рекурсивно строим подкоманду
    team_members: List[Member] = [build_member_from_payload(m) for m in team_data]

    return Member(name=name, lo=lo, team=team_members)
