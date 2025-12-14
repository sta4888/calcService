from typing import List

from app.domain.exceptions import InvalidVolumeError


class Member:
    def __init__(self, name: str, lo: float, team: List["Member"] | None = None):
        if lo < 0:
            raise InvalidVolumeError("LO cannot be negative")
        self.name = name
        self.lo = lo
        self.team = team or []

    def group_volume(self) -> float:
        return self.lo + sum(m.group_volume() for m in self.team)
