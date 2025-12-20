from dataclasses import dataclass

@dataclass(frozen=True)
class Qualification:
    name: str
    min_points: int
    personal_percent: float
    team_percent: float
    mentor_percent: float
    extra_bonus: str
