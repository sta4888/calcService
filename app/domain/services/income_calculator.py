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

    Правило командного — "представители подветки":
      Для каждого прямого ребёнка root_child:
        - если root_child сильная (q >= итог родителя) → в лидерский
        - иначе спускаемся и собираем "представителей":
          представитель = узел, под которым нет никого сильнее его
          (сравнение по team_percent).
          С каждого представителя берём GO × (parent% − rep%) × 7000.

    Hamkor-листья: сейчас включаются как представители (с полным diff).
    Если нужно их пропускать — раскомментировать фильтр в _collect_reps.
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

        # 1) Свой LO × свой team_percent
        if member.lo > 0 and member_q.team_percent > 0:
            own_money = member.lo * member_q.team_percent * VERON_PRICE
            total += own_money
            items.append(BreakdownItem(
                description=f"Свой LO × {member_q.team_percent * 100:.0f}%",
                volume=member.lo,
                percent=member_q.team_percent,
                money=own_money,
            ))

        # 2) По каждой прямой ветке — собираем представителей и
        #    с каждого берём GO × diff
        for child in member.team:
            child_q = self._resolver.qualify(child)

            # Сильные ветки → в лидерский, не сюда
            if child_q.min_points >= member_q.min_points:
                continue

            # Собираем представителей из этой подветки
            representatives = self._collect_reps(child)

            for rep in representatives:
                rep_q = self._resolver.qualify(rep)
                diff = member_q.team_percent - rep_q.team_percent
                if diff <= 0:
                    continue

                rep_go = rep.group_volume()
                if rep_go == 0:
                    continue

                money = rep_go * diff * VERON_PRICE
                total += money
                items.append(BreakdownItem(
                    description=(
                        f"С {rep_q.name} (ID:{rep.user_id}) – "
                        f"{diff * 100:.1f}%"
                    ),
                    volume=rep_go,
                    percent=diff,
                    money=money,
                ))

        return total, items

    def _collect_reps(self, node: Member) -> List[Member]:
        """
        Собирает "представителей" подветки.
        Представитель = узел, под которым НЕТ никого сильнее его самого.
        Если под node есть кто-то сильнее — node "не лидер",
        собираем представителей с его детей.

        ЗАМЕТКА: чтобы пропускать Hamkor-узлы (включать только
        тех, кто закрыл хотя бы Mentor) — раскомментировать
        фильтр ниже.
        """
        node_q = self._resolver.qualify(node)

        if self._has_stronger_descendant(node, node_q.team_percent):
            # node не лидер своей подветки — спускаемся к детям
            result: List[Member] = []
            for child in node.team:
                result.extend(self._collect_reps(child))
            return result

        # node — лидер своей подветки
        # # Если нужно пропускать Hamkor (только закрывшие Mentor+):
        # if node_q.min_points < MENTOR.min_points:
        #     return []
        return [node]

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
