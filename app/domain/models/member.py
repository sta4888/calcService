from typing import List

class Member:
    def __init__(self, name: str, lo: float, team: List["Member"] | None = None):
        self.name = name
        self.lo = lo
        self.team = team or []

    def group_volume(self) -> float:
        return self.lo + sum(m.group_volume() for m in self.team)