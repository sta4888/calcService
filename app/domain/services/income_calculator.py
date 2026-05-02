# -*- coding: utf-8 -*-
from typing import List, Tuple

from domain.models.member import Member
from domain.value_objects.BreakdownItem import BreakdownItem
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import QUALIFICATIONS

from domain.services.qualification_resolver import QualificationResolver


VERON_PRICE = 7000
MENTOR = QUALIFICATIONS[1]


class IncomeCalculator:
    """
    Считает три типа дохода: личный, командный, лидерский.

    Правила:
    1. Личный: LO × q.personal_percent × VERON_PRICE.
    2. Прямые дети делятся на две группы:
       - Сильные (квалификация >= итоговой родителя)  → идут в лидерский
       - Обычные (квалификация <  итоговой родителя)  → идут в командный
    3. Командный: для каждой обычной ветки c
           diff = q.team_percent - c_q.team_percent
           если diff > 0: money += c.GO × diff × VERON_PRICE
    4. Лидерский: только если q >= Mentor
           money = sum(GO сильных веток) × q.mentor_percent × VERON_PRICE
    """

    def __init__(self, resolver: QualificationResolver):
        self._resolver = resolver

    # =================================================================
    # ЛИЧНЫЙ
    # =================================================================

    def personal(
            self, member: Member, q: Qualification
    ) -> Tuple[float, BreakdownItem]:
        money = member.lo * q.personal_percent * VERON_PRICE
        item = BreakdownItem(
            description=f"Личный объём – {q.personal_percent * 100:.0f}%",
            volume=member.lo,
            percent=q.personal_percent,
            money=money,
        )
        return money, item

    # =================================================================
    # КОМАНДНЫЙ (только с обычных веток)
    # =================================================================

    def team(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        total = 0.0
        items: List[BreakdownItem] = []

        for child in member.team:
            child_q = self._resolver.qualify(child)

            # Сильные ветки в командный не попадают — они для лидерского
            if child_q.min_points >= member_q.min_points:
                continue

            diff = member_q.team_percent - child_q.team_percent
            if diff <= 0:
                continue

            child_go = child.group_volume()
            if child_go == 0:
                continue

            money = child_go * diff * VERON_PRICE
            total += money
            items.append(BreakdownItem(
                description=(
                    f"С {child_q.name} (ID:{child.user_id}) – "
                    f"{diff * 100:.1f}%"
                ),
                volume=child_go,
                percent=diff,
                money=money,
            ))

        return total, items

    # =================================================================
    # ЛИДЕРСКИЙ (с сильных веток)
    # =================================================================

    def leader(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        # Условие: сам как минимум Mentor
        if member_q.min_points < MENTOR.min_points:
            return 0.0, []

        # Сумма GO сильных веток (квалификация >= итоговой родителя)
        strong_go = 0.0
        for child in member.team:
            child_q = self._resolver.qualify(child)
            if child_q.min_points >= member_q.min_points:
                strong_go += child.group_volume()

        if strong_go == 0:
            return 0.0, []

        money = strong_go * member_q.mentor_percent * VERON_PRICE
        item = BreakdownItem(
            description=(
                f"С сильных веток – {member_q.mentor_percent * 100:.0f}%"
            ),
            volume=strong_go,
            percent=member_q.mentor_percent,
            money=money,
        )
        return money, [item]