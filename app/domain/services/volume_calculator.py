# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING
from domain.models.member import Member
from domain.value_objects.qualification import Qualification

if TYPE_CHECKING:
    from domain.services.qualification_resolver import QualificationResolver


class VolumeCalculator:
    """
    Считает объёмы по дереву участников.

    Сильная ветка — прямой ребёнок, чья квалификация >= q_pot.
    Чтобы определить квалификацию ребёнка, обращается к QualificationResolver.
    """

    def __init__(self, resolver: "QualificationResolver"):
        self._resolver = resolver

    def group_volume(self, member: Member) -> float:
        """Полный GO: LO + сумма GO всех детей."""
        return member.group_volume()

    def clean_go(self, member: Member, q_pot: Qualification) -> float:
        """GO без сильных веток (детей с квалификацией >= q_pot)."""
        total = self.group_volume(member)
        for child in member.team:
            child_q = self._resolver.qualify(child)
            if child_q.min_points >= q_pot.min_points:
                total -= child.group_volume()
        return total

    def clean_yonbosh(self, member: Member, q_pot: Qualification) -> float:
        """Yonbosh без сильных веток: LO + GO детей слабее q_pot."""
        total = member.lo
        for child in member.team:
            child_q = self._resolver.qualify(child)
            if child_q.min_points < q_pot.min_points:
                total += child.group_volume()
        return total

    def strong_branches_go(self, member: Member, q: Qualification) -> float:
        """Сумма GO веток с квалификацией >= q. Используется для лидерского."""
        total = 0.0
        for child in member.team:
            child_q = self._resolver.qualify(child)
            if child_q.min_points >= q.min_points:
                total += child.group_volume()
        return total
