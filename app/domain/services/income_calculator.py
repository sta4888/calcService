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

    def team(self, member, member_q):
        if member_q.team_percent <= 0:
            return 0.0, []

        items = []
        money = member.lo * member_q.team_percent * VERON_PRICE
        items.append(BreakdownItem(
            description=f"Личный объём – {member_q.team_percent * 100:.0f}%",
            volume=member.lo,
            percent=member_q.team_percent,
            money=money,
        ))

        # Каждый узел поддерева платит member разницу (tp_member - tp_node)
        # со своего up_value, ЕСЛИ member — его ближайший уплайн со строго
        # большим team_percent. Идём снизу вверх: узел "закрывается" на
        # первом предке, чей tp строго выше.
        def collect(node, blocked_percent):
            """
            blocked_percent — максимальный tp среди предков МЕЖДУ node и member.
            Если у какого-то промежуточного предка tp >= tp(node), то node
            платит ЕМУ, а не member → сюда не попадает.
            """
            nq = self._resolver.qualify(node)
            # node платит member только если между ними нет предка с tp > tp(node)
            if nq.team_percent < member_q.team_percent and blocked_percent <= nq.team_percent:
                diff = member_q.team_percent - nq.team_percent
                vol = self._resolver.up_value(node)
                if vol > 0 and diff > 0:
                    m = vol * diff * VERON_PRICE
                    nonlocal money
                    money += m
                    items.append(BreakdownItem(
                        description=f"С ветки {nq.name} (ID:{node.user_id}) – {diff * 100:.0f}%",
                        volume=vol,
                        percent=diff,
                        money=m,
                    ))
            # спускаемся: обновляем "потолок" перекрытия
            child_blocked = max(blocked_percent, nq.team_percent)
            for c in node.team:
                collect(c, child_blocked)

        for child in member.team:
            collect(child, 0.0)

        return money, items

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
            # та же граница, что и в clean_go: Mentor+ с рангом >= нашего
            # отвалился из чистого ГО → за него идёт лидерский овердайд
            broke_away = (
                child_q.min_points >= MENTOR.min_points
                and child_q.min_points >= member_q.min_points
            )
            if broke_away:
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