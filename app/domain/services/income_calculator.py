from domain.value_objects.levels import level_by_volume
from web.scheme.schemas import IncomeResponse

class IncomeCalculator:
    def calculate(self, root):

        root_level = level_by_volume(root.group_volume())

        personal_bonus = root.lo * root_level.percent
        structure_bonus = sum(
            self._structure_bonus(member, root_level) for member in root.team
        )

        return IncomeResponse(
            name=root.name,
            lo=root.lo,
            go=root.group_volume(),
            level=root_level.percent,
            personal_bonus=personal_bonus,
            structure_bonus=structure_bonus,
            total_income=personal_bonus + structure_bonus,
        )

    def _structure_bonus(self, member, upline_level):
        my_level = level_by_volume(member.group_volume())
        diff = upline_level.diff(my_level) or 0  # защита на None
        bonus = member.group_volume() * diff
        deep = sum(self._structure_bonus(child, my_level) for child in member.team)
        return bonus + deep
