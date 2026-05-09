# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING
from domain.models.member import Member
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import QUALIFICATIONS  # ← убедись что есть

if TYPE_CHECKING:
    from domain.services.qualification_resolver import QualificationResolver


HAMKOR = QUALIFICATIONS[0]
MENTOR = QUALIFICATIONS[1]


class VolumeCalculator:
    def __init__(self, resolver: "QualificationResolver"):
        self._resolver = resolver

    def group_volume(self, member: Member) -> float:
        return member.group_volume()

    def yonbosh(self, member: Member) -> float:
        """LO + GO детей-Hamkor (квалификация < Mentor)."""
        total = member.lo
        for child in member.team:
            child_q = self._resolver.qualify(child)
            if child_q.min_points < MENTOR.min_points:
                total += child.group_volume()
        return total

    def gsv(self, member: Member) -> float:
        """
        Group Side Volume = полный GO − GO прямых сильных детей.
        "Сильный" = квалификация >= потенциальной квалификации родителя
        (по полному GO).
        """
        total_go = self.group_volume(member)
        q_pot = self._potential(total_go)

        if q_pot is HAMKOR:
            return total_go

        for child in member.team:
            child_q = self._resolver.qualify(child)
            if child_q.min_points >= q_pot.min_points:
                total_go -= child.group_volume()

        return total_go

    def _potential(self, group_volume: float) -> Qualification:
        """Самая высокая квалификация под полный GO."""
        for q in reversed(QUALIFICATIONS):
            if group_volume >= q.min_points:
                return q
        return HAMKOR

    def clean_go(self, member: Member, q_pot: Qualification) -> float:
        """GO без сильных веток (для использования в QualificationResolver)."""
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