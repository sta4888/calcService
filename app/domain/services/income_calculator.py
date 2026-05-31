# -*- coding: utf-8 -*-
from typing import List, Tuple

from domain.models.member import Member
from domain.value_objects.BreakdownItem import BreakdownItem
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import QUALIFICATIONS

from domain.services.qualification_resolver import QualificationResolver

VERON_PRICE = 7000
HAMKOR = QUALIFICATIONS[0]
MENTOR = QUALIFICATIONS[1]


class IncomeCalculator:
    """
    Три дохода, все на одном примитиве clean_go / up_value:

      ЛИЧНЫЙ   = LO × personal_percent × PRICE

      КОМАНДНЫЙ = clean_go(member, ранг) × team_percent × PRICE
                  clean_go — это чистый ГО члена: его LO + поднятые объёмы
                  всех веток, кроме тех, что строго сильнее (они отвалились).

      ЛИДЕРСКИЙ = sum(up_value прямых веток, строго сильнее члена)
                  × mentor_percent × PRICE
                  (только если член ≥ Mentor)

    ВАЖНО про модель командных:
      Здесь член получает ПОЛНЫЙ team_percent на весь свой чистый ГО
      (unilevel со сжатием) — ровно то, о чём договорились (2980 × team%).
      Если по плану нужна ДИФФЕРЕНЦИАЛЬНАЯ схема (каждый аплайн получает
      только РАЗНИЦУ % над нижестоящим лидером) — это меняет team()/leader(),
      скажи, и я переключу.
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
    # КОМАНДНЫЙ — на чистом GO
    # =================================================================

    def team(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        if member_q.team_percent <= 0:
            return 0.0, []

        base = self._resolver.clean_go(member, member_q)
        money = base * member_q.team_percent * VERON_PRICE
        item = BreakdownItem(
            description=f"Чистый ГО × {member_q.team_percent * 100:.0f}%",
            volume=base,
            percent=member_q.team_percent,
            money=money,
        )
        return money, [item]

    # =================================================================
    # ЛИДЕРСКИЙ — на отвалившихся (строго сильных) прямых ветках
    # =================================================================

    def leader(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        if member_q.min_points < MENTOR.min_points:
            return 0.0, []

        items: List[BreakdownItem] = []
        money = 0.0
        for child in member.team:
            child_q = self._resolver.qualify(child)
            # строго сильнее → ветка отвалилась из чистого ГО → овердайд
            if child_q.min_points > member_q.min_points:
                vol = self._resolver.up_value(child)
                m = vol * member_q.mentor_percent * VERON_PRICE
                money += m
                items.append(BreakdownItem(
                    description=(
                        f"С ветки {child_q.name} (ID:{child.user_id}) – "
                        f"{member_q.mentor_percent * 100:.0f}%"
                    ),
                    volume=vol,
                    percent=member_q.mentor_percent,
                    money=m,
                ))

        return money, items