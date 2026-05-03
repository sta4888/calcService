# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING
from domain.models.member import Member
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import QUALIFICATIONS

if TYPE_CHECKING:
    from domain.services.qualification_resolver import QualificationResolver

MENTOR = QUALIFICATIONS[1]


class VolumeCalculator:
    """
    Считает объёмы по дереву.

    yonbosh = LO + сумма GO детей-Hamkor (тех, кто НЕ закрыл Mentor).
    """

    def __init__(self, resolver: "QualificationResolver"):
        self._resolver = resolver

    def group_volume(self, member: Member) -> float:
        return member.group_volume()

    def yonbosh(self, member: Member) -> float:
        """LO + рекурсивная сумма contribution от детей."""
        total = member.lo
        for child in member.team:
            total += self._contribution(child)
        return total

    def _contribution(self, branch: Member) -> float:
        """
        Что ветка вносит в yonbosh родителя:
        - 0, если закрыла Mentor
        - иначе её LO + рекурсивно contribution её детей
        """
        branch_q = self._resolver.qualify(branch)
        if branch_q.min_points >= MENTOR.min_points:
            return 0.0

        own = branch.lo
        for child in branch.team:
            own += self._contribution(child)
        return own

    def clean_go(self, member: Member, q_pot: Qualification) -> float:
        """GO без сильных веток (детей с квалификацией >= q_pot)."""
        total = self.group_volume(member)
        for child in member.team:
            child_q = self._resolver.qualify(child)
            if child_q.min_points >= q_pot.min_points:
                total -= child.group_volume()
        return total

    def strong_branches_go(self, member: Member, q: Qualification) -> float:
        """Сумма GO веток с квалификацией >= q."""
        total = 0.0
        for child in member.team:
            child_q = self._resolver.qualify(child)
            if child_q.min_points >= q.min_points:
                total += child.group_volume()
        return total
