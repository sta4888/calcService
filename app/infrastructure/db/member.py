from typing import List
from dataclasses import dataclass

@dataclass
class Member:
    user_id: int
    referrer_id: int | None
    lo: float = 0
    team: List["Member"] = None

    def __post_init__(self):
        if self.team is None:
            self.team = []

    def group_volume(self) -> float:
        return self.lo + sum(member.group_volume() for member in self.team)
