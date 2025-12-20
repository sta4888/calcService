from domain.value_objects.qualifications import qualification_by_points
from web.scheme.schemas import IncomeResponse

VERON_PRICE = 7000

class IncomeCalculator:

    def calculate(self, member):
        # ГО
        group_volume = member.group_volume()

        # Баллы = ГО
        points = int(group_volume)

        # Статус
        qualification = qualification_by_points(points)

        # ===== Денежные бонусы =====

        # Личный бонус (деньги)
        personal_bonus = member.lo * qualification.personal_percent * VERON_PRICE

        # Командный оборот
        team_volume = max(group_volume - member.lo, 0)

        # Командный бонус (деньги)
        team_bonus = team_volume * qualification.team_percent * VERON_PRICE

        # ===== Veron =====

        # Veron за личный объём
        veron_personal = member.lo * qualification.personal_percent

        # Veron за групповой объём
        veron_team = group_volume * qualification.team_percent

        veron_total = veron_personal + veron_team
        veron_money = veron_total * VERON_PRICE

        # ===== Наставничество =====

        mentor_bonus = group_volume * qualification.mentor_percent * VERON_PRICE

        # ===== Итого =====

        total_income = (
            veron_money +
            mentor_bonus
        )

        return IncomeResponse(
            user_id=member.user_id,
            qualification=qualification.name,
            lo=member.lo,
            go=team_volume,
            points=points,
            personal_bonus=personal_bonus,
            structure_bonus=team_bonus,
            mentor_bonus=mentor_bonus,
            extra_bonus=qualification.extra_bonus,
            veron=veron_money,
            total_income=total_income
        )
