from typing import List, Optional
from domain.exceptions import InvalidVolumeError

from domain.value_objects.qualifications import qualification_by_points

SIDE_VOLUME_THRESHOLD = 500

class Member:
    def __init__(
        self,
        user_id: int,
        referrer_id: Optional[int] = None,
        lo: float = 0,
        team: List["Member"] | None = None,
    ):
        if lo < 0:
            raise InvalidVolumeError("LO cannot be negative")

        self.user_id = user_id
        self.referrer_id = referrer_id
        self.lo = lo
        self.team = team or []

    def group_volume(self) -> float:
        return self.lo + sum(m.group_volume() for m in self.team)

    def __repr__(self) -> str:
        return (
            f"Member("
            f"user_id={self.user_id}, "
            f"referrer_id={self.referrer_id}, "
            f"lo={self.lo}, "
            f"team_size={len(self.team)}"
            f")"
        )

