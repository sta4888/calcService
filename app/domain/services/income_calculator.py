from domain.value_objects.levels import level_by_volume, qualification_by_percent
from web.scheme.schemas import IncomeResponse

class IncomeCalculator:
    def calculate(self, member):
        # уровень по групповому объёму
        level = level_by_volume(member.group_volume())
        qual = qualification_by_percent(level.percent)

        personal_bonus = member.lo * level.percent
        structure_bonus = sum(self._structure_bonus(child, level) for child in member.team)

        points = self._calc_points(member.lo)
        veron = self._calc_veron(points, level.percent)

        return IncomeResponse(
            user_id=member.user_id,
            lo=member.lo,
            go=member.group_volume(),
            level=level.percent,
            qualification=qual,
            personal_bonus=personal_bonus,
            structure_bonus=structure_bonus,
            total_income=personal_bonus + structure_bonus,
            points=points,
            veron=veron
        )

    def _structure_bonus(self, member, upline_level):
        my_level = level_by_volume(member.group_volume())
        diff = upline_level.diff(my_level) or 0
        bonus = member.group_volume() * diff
        deep = sum(self._structure_bonus(child, my_level) for child in member.team)
        return bonus + deep

    def _calc_points(self, lo: float) -> float:
        return lo / 15000

    def _calc_veron(self, points: float, percent: float) -> float:
        return points * (1 + percent) * 7000

