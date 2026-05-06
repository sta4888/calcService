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

    Командный = две части:
      1) yonbosh × q.team_percent × VERON_PRICE
         где yonbosh = LO + рекурсивная сумма contribution(Hamkor-веток)
            contribution(node):
                - Mentor+ → 0 (граница)
                - Hamkor  → LO + sum(contribution(детей))

      2) Для каждого прямого ребёнка:
         - сильный (q ≥ родителя) → пропуск (в лидерский)
         - иначе → рекурсивный обход подветки по правилу "лидер/не-лидер":
             узел Hamkor → не вносит вклада, идём в детей
             узел Mentor+ "лидер" (под ним нет сильнее) → GO × diff, не идём вглубь
             узел Mentor+ "не-лидер" (под ним есть сильнее) → LO × diff, идём вглубь
           где diff = q.team_percent − node.team_percent

    Лидерский: только если q ≥ Mentor.
        sum(GO сильных детей) × q.mentor_percent × VERON_PRICE
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
    # КОМАНДНЫЙ
    # =================================================================

    def team(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        total = 0.0
        items: List[BreakdownItem] = []

        # --- 1) yonbosh × q.team_percent ---
        yonbosh = self._yonbosh_value(member)
        if yonbosh > 0 and member_q.team_percent > 0:
            yb_money = yonbosh * member_q.team_percent * VERON_PRICE
            total += yb_money
            items.append(BreakdownItem(
                description=f"Yonbosh × {member_q.team_percent * 100:.0f}%",
                volume=yonbosh,
                percent=member_q.team_percent,
                money=yb_money,
            ))

        # --- 2) Прямые дети ---
        for child in member.team:
            child_q = self._resolver.qualify(child)

            # Сильные → в лидерский
            if child_q.min_points >= member_q.min_points:
                continue

            # Рекурсивный обход подветки
            child_money, child_items = self._walk_subtree(child, member_q)
            total += child_money
            items.extend(child_items)

        return total, items

    def _walk_subtree(
            self, node: Member, parent_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        """
        Рекурсивно проходит подветку и собирает вклады по правилу
        "лидер/не-лидер".
        """
        money = 0.0
        items: List[BreakdownItem] = []
        node_q = self._resolver.qualify(node)

        if node_q.min_points < MENTOR.min_points:
            # Hamkor — не вносит вклад, но идём в детей
            for child in node.team:
                cm, ci = self._walk_subtree(child, parent_q)
                money += cm
                items.extend(ci)
            return money, items

        # node закрыл Mentor+
        diff = parent_q.team_percent - node_q.team_percent
        if diff <= 0:
            # node сильнее или равен parent — не должно случиться,
            # т.к. сильные ветки отсечены выше. На всякий случай идём дальше.
            for child in node.team:
                cm, ci = self._walk_subtree(child, parent_q)
                money += cm
                items.extend(ci)
            return money, items

        if self._has_stronger_descendant(node, node_q.team_percent):
            # Не-лидер — вносит LO, идём вглубь
            if node.lo > 0:
                m = node.lo * diff * VERON_PRICE
                money += m
                items.append(BreakdownItem(
                    description=(
                        f"С {node_q.name} (ID:{node.user_id}, не-лидер) – "
                        f"LO × {diff * 100:.1f}%"
                    ),
                    volume=node.lo,
                    percent=diff,
                    money=m,
                ))
            for child in node.team:
                cm, ci = self._walk_subtree(child, parent_q)
                money += cm
                items.extend(ci)
        else:
            # Лидер — вносит GO, дальше не идём
            node_go = node.group_volume()
            if node_go > 0:
                m = node_go * diff * VERON_PRICE
                money += m
                items.append(BreakdownItem(
                    description=(
                        f"С {node_q.name} (ID:{node.user_id}, лидер) – "
                        f"GO × {diff * 100:.1f}%"
                    ),
                    volume=node_go,
                    percent=diff,
                    money=m,
                ))

        return money, items

    # =================================================================
    # ВСПОМОГАТЕЛЬНЫЕ
    # =================================================================

    def _yonbosh_value(self, member: Member) -> float:
        """LO + рекурсивная сумма contribution(прямых детей)."""
        total = float(member.lo)
        for child in member.team:
            total += self._contribution(child)
        return total

    def _contribution(self, node: Member) -> float:
        """
        - Mentor+ → 0 (граница)
        - Hamkor  → LO + sum(contribution детей)
        """
        node_q = self._resolver.qualify(node)
        if node_q.min_points >= MENTOR.min_points:
            return 0.0
        total = float(node.lo)
        for child in node.team:
            total += self._contribution(child)
        return total

    def _has_stronger_descendant(
            self, node: Member, threshold_percent: float
    ) -> bool:
        """Есть ли в поддереве node (исключая сам node) узел
        с team_percent > threshold?"""
        for child in node.team:
            child_q = self._resolver.qualify(child)
            if child_q.team_percent > threshold_percent:
                return True
            if self._has_stronger_descendant(child, threshold_percent):
                return True
        return False

    # =================================================================
    # ЛИДЕРСКИЙ
    # =================================================================

    def leader(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        if member_q.min_points < MENTOR.min_points:
            return 0.0, []

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