# -*- coding: utf-8 -*-
from typing import List, Tuple, Iterable

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

    Командный — правило "вкладов в подветке":
      Для каждого прямого ребёнка root_child:
        - сильная (q >= итог родителя) → в лидерский, не сюда
        - иначе спускаемся и собираем вклады по правилу:

          Для каждого узла node в подветке:
            * если node Hamkor → не вносит вклад, но идём в его детей
            * если node закрыл Mentor+:
                - если под node есть кто-то СИЛЬНЕЕ (по team_percent):
                    node "не лидер" → вносит вклад через свой LO
                    + идём в его детей искать дальше
                - если под node никого сильнее:
                    node "лидер" своей подветки → вносит вклад через свой GO
                    + НЕ идём в его детей (всё внутри уже учтено в GO)

      С каждого вклада: объём × (parent_team_percent − node_team_percent) × VERON_PRICE.

      Плюс свой LO родителя × parent_team_percent × VERON_PRICE.
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

        # 1) Свой LO родителя × свой team_percent
        if member.lo > 0 and member_q.team_percent > 0:
            own_money = member.lo * member_q.team_percent * VERON_PRICE
            total += own_money
            items.append(BreakdownItem(
                description=f"Свой LO × {member_q.team_percent * 100:.0f}%",
                volume=member.lo,
                percent=member_q.team_percent,
                money=own_money,
            ))

        # 2) По каждой прямой ветке — собираем вклады
        for child in member.team:
            child_q = self._resolver.qualify(child)

            # Сильные ветки → в лидерский, не сюда
            if child_q.min_points >= member_q.min_points:
                continue

            for contributor, volume, contributor_q in self._collect_contributions(child):
                diff = member_q.team_percent - contributor_q.team_percent
                if diff <= 0:
                    continue
                if volume == 0:
                    continue

                money = volume * diff * VERON_PRICE
                total += money
                items.append(BreakdownItem(
                    description=(
                        f"С {contributor_q.name} (ID:{contributor.user_id}) – "
                        f"{diff * 100:.1f}%"
                    ),
                    volume=volume,
                    percent=diff,
                    money=money,
                ))

        return total, items

    def _collect_contributions(
            self, node: Member
    ) -> Iterable[Tuple[Member, float, Qualification]]:
        """
        Возвращает список (узел, объём, его_квалификация) для всех вкладчиков
        в подветке node.

        Hamkor: пропускается (не вносит вклада), но рекурсивно идём в его детей.
        Mentor+ "лидер" (под ним нет сильнее): вносит GO, дальше не идём.
        Mentor+ "не лидер" (под ним есть сильнее): вносит LO, идём дальше.
        """
        node_q = self._resolver.qualify(node)

        # Hamkor — без вклада, но идём в детей
        if node_q.min_points < MENTOR.min_points:
            for child in node.team:
                yield from self._collect_contributions(child)
            return

        # node закрыл Mentor+
        if self._has_stronger_descendant(node, node_q.team_percent):
            # Не лидер — вносит свой LO, продолжаем спуск
            yield (node, float(node.lo), node_q)
            for child in node.team:
                yield from self._collect_contributions(child)
        else:
            # Лидер своей подветки — вносит свой GO, спуск прерываем
            yield (node, node.group_volume(), node_q)

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
        # Только если сам Mentor или выше
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
