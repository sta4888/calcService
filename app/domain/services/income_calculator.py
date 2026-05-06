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

    Командный = три части:
      1) yonbosh самого участника × parent.team_percent × VERON_PRICE
         где yonbosh = LO + рекурсивная сумма contribution(Hamkor-веток)
      2) С каждой Hamkor-подветки (прямой ребёнок-Hamkor):
         (GO − contribution_yonbosh) × (parent% − max_team_in_subtree) × VERON_PRICE
      3) С каждой не-Hamkor обычной ветки (квалификация ≥ Mentor, но < parent):
         GO × (parent% − child%) × VERON_PRICE
      Сильные ветки (≥ parent) → не в командный, в лидерский.
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

        # --- 1) yonbosh × parent.team_percent ---
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

        # --- 2 & 3) Прямые дети ---
        for child in member.team:
            child_q = self._resolver.qualify(child)

            # Сильные → в лидерский
            if child_q.min_points >= member_q.min_points:
                continue

            child_go = child.group_volume()

            if child_q.min_points < MENTOR.min_points:
                # === Hamkor-ветка: (GO − contribution) × (parent% − max%) ===
                contribution = self._contribution(child)
                remainder = child_go - contribution
                if remainder <= 0:
                    continue

                max_pct = self._max_team_percent_in_subtree(child)
                diff = member_q.team_percent - max_pct
                if diff <= 0:
                    continue

                money = remainder * diff * VERON_PRICE
                total += money
                items.append(BreakdownItem(
                    description=(
                        f"Остаток Hamkor-ветки {child.user_id} "
                        f"(GO−yonbosh) × {diff * 100:.1f}%"
                    ),
                    volume=remainder,
                    percent=diff,
                    money=money,
                ))
            else:
                # === Обычная не-Hamkor ветка: GO × (parent% − child%) ===
                diff = member_q.team_percent - child_q.team_percent
                if diff <= 0 or child_go == 0:
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
    # ВСПОМОГАТЕЛЬНЫЕ ДЛЯ КОМАНДНОГО
    # =================================================================

    def _yonbosh_value(self, member: Member) -> float:
        """LO + рекурсивная сумма contribution(прямых детей)."""
        total = float(member.lo)
        for child in member.team:
            total += self._contribution(child)
        return total

    def _contribution(self, node: Member) -> float:
        """
        Рекурсивная contribution в yonbosh:
        - если node закрыл Mentor+ → 0 (граница)
        - иначе → LO + сумма contribution детей
        """
        node_q = self._resolver.qualify(node)
        if node_q.min_points >= MENTOR.min_points:
            return 0.0

        total = float(node.lo)
        for child in node.team:
            total += self._contribution(child)
        return total

    def _max_team_percent_in_subtree(self, node: Member) -> float:
        """
        Максимальный team_percent среди всех узлов в подветке node
        (включая саму node).
        """
        node_q = self._resolver.qualify(node)
        max_pct = node_q.team_percent
        for child in node.team:
            child_max = self._max_team_percent_in_subtree(child)
            if child_max > max_pct:
                max_pct = child_max
        return max_pct

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