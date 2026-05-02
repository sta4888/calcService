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
    Нужна QualificationResolver, чтобы получать квалификации детей.
    """

    def __init__(self, resolver: QualificationResolver):
        self._resolver = resolver

    # --- личный ---

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

    # --- командный (с прямых детей × GO) ---

    def team(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        """
        Для каждого прямого ребёнка c:
            diff = member_q.team_percent - c_q.team_percent
            если diff > 0: money += c.GO × diff × VERON_PRICE
        """
        total = 0.0
        items: List[BreakdownItem] = []

        for child in member.team:
            child_q = self._resolver.qualify(child)
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

    # --- лидерский (с сильных веток) ---

    def leader(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        if member_q.min_points < MENTOR.min_points:
            return 0.0, []

        strong_go = self._resolver.volume.strong_branches_go(member, member_q)
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
