from domain.models.member import SIDE_VOLUME_THRESHOLD
from domain.value_objects.qualifications import qualification_by_points
from web.scheme.schemas import IncomeResponse

VERON_PRICE = 7000


class IncomeCalculator:

    def calculate(self, member):
        group_volume = member.group_volume()
        side_volume = member.side_volume()

        # квалификация определяется ОДИН раз
        if side_volume >= SIDE_VOLUME_THRESHOLD:
            points = int(group_volume)
        else:
            points = int(side_volume)

        qualification = qualification_by_points(points)

        personal_bonus = (
            member.lo * qualification.personal_percent * VERON_PRICE
        )

        team_volume = max(group_volume - member.lo, 0)

        team_bonus = (
            team_volume * qualification.team_percent * VERON_PRICE
        )

        mentor_bonus = (
            group_volume * qualification.mentor_percent * VERON_PRICE
        )

        total_income = personal_bonus + team_bonus + mentor_bonus

        return IncomeResponse(
            user_id=member.user_id,
            qualification=qualification.name,
            lo=member.lo,
            go=team_volume,
            points=points,
            personal_bonus=personal_bonus,
            structure_bonus=team_bonus,
            mentor_bonus=mentor_bonus,
            side_volume=side_volume,
            extra_bonus=qualification.extra_bonus,
            veron=personal_bonus + team_bonus,
            total_income=total_income,
        )
