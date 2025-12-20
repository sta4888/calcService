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

    def branch_volumes(self) -> list[float]:
        return [m.group_volume() for m in self.team]

    def side_volume(self) -> float:
        """
        Боковой объём = LO + объёмы веток,
        которые НЕ закрыли квалификацию
        """
        side = self.lo

        for branch in self.team:
            branch_gv = branch.group_volume()
            branch_side = branch.side_volume()

            qualification = qualification_by_points(int(branch_gv))

            is_side_closed = (
                branch_side >= SIDE_VOLUME_THRESHOLD
                and qualification.name != "Hamkor"
            )

            if not is_side_closed:
                side += branch_gv

        return side


