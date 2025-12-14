from typing import List, Optional
from domain.exceptions import InvalidVolumeError

class Member:
    def __init__(self, user_id: int, referrer_id: Optional[int] = None, lo: float = 0, team: List["Member"] | None = None):
        if lo < 0:
            raise InvalidVolumeError("LO cannot be negative")
        self.user_id = user_id
        self.referrer_id = referrer_id
        self.lo = lo
        self.team = team or []

    def add_lo(self, value: float):
        if value < 0:
            raise InvalidVolumeError("LO must be positive")
        self.lo += value

    def group_volume(self) -> float:
        return self.lo + sum(m.group_volume() for m in self.team)
