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

    Принцип:
    - Прямые дети делятся на сильные и обычные:
        сильная: c.q >= итоговая родителя → идёт в лидерский
        обычная: c.q <  итоговая родителя → идёт в командный
    - Каждый рубль платится один раз (farq foizi).

    Формулы:
        personal = LO × q.personal_percent × VERON_PRICE

        team =   LO × q.team_percent × VERON_PRICE                # за свой LO
               + sum(c.GO × (q.team_percent − c.q.team_percent)   # за обычных
                     × VERON_PRICE) для обычных детей с diff > 0

        leader = sum(GO сильных детей) × q.mentor_percent × VERON_PRICE
                 (только если q >= Mentor)
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
    # КОМАНДНЫЙ — LO родителя × свой % + diff с обычных детей
    # =================================================================

    def team(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        print(f"\n=== TEAM для id={member.user_id} q={member_q.name} t%={member_q.team_percent} ===")
        total = 0.0
        items: List[BreakdownItem] = []

        # 1) Свой LO × свой team_percent (LO принадлежит самому родителю)
        if member.lo > 0 and member_q.team_percent > 0:
            own_money = member.lo * member_q.team_percent * VERON_PRICE
            print(f"  свой LO: {member.lo} × {member_q.team_percent} × 7000 = {own_money}")
            total += own_money
            items.append(BreakdownItem(
                description=(
                    f"Свой LO × {member_q.team_percent * 100:.0f}%"
                ),
                volume=member.lo,
                percent=member_q.team_percent,
                money=own_money,
            ))

        # 2) С каждой обычной ветки — разница процентов × GO ветки
        for child in member.team:
            child_q = self._resolver.qualify(child)
            is_strong = child_q.min_points >= member_q.min_points
            diff = member_q.team_percent - child_q.team_percent
            child_go = child.group_volume()
            print(f"  ребёнок id={child.user_id} q={child_q.name} GO={child_go} "
                  f"{'СИЛЬНАЯ' if is_strong else f'обычная diff={diff}'}")
            if is_strong: continue
            if diff <= 0: continue
            if child_go == 0: continue
            money = child_go * diff * VERON_PRICE
            print(f"     → {child_go} × {diff} × 7000 = {money}")
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
    # ЛИДЕРСКИЙ — с сильных веток
    # =================================================================

    def leader(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        # Только если сам Mentor или выше
        print(f"\n=== LEADER для id={member.user_id} q={member_q.name} m%={member_q.mentor_percent} ===")
        if member_q.min_points < MENTOR.min_points:
            print(f"  q < Mentor → 0")
            return 0.0, []

        strong_go = 0.0
        for child in member.team:
            child_q = self._resolver.qualify(child)
            if child_q.min_points >= member_q.min_points:
                print(f"  сильный ребёнок id={child.user_id} q={child_q.name} GO={child.group_volume()}")
                strong_go += child.group_volume()

        print(f"  strong_go = {strong_go}")
        money = strong_go * member_q.mentor_percent * VERON_PRICE
        print(f"  leader = {strong_go} × {member_q.mentor_percent} × 7000 = {money}")
        item = BreakdownItem(
            description=(
                f"С сильных веток – {member_q.mentor_percent * 100:.0f}%"
            ),
            volume=strong_go,
            percent=member_q.mentor_percent,
            money=money,
        )
        return money, [item]
