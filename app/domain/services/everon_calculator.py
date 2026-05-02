# -*- coding: utf-8 -*-
from domain.models.member import Member
from domain.value_objects.BreakdownItem import IncomeBreakdown
from domain.value_objects.qualifications import QUALIFICATIONS
from web.scheme.schemas import IncomeResponse

from domain.services.qualification_resolver import QualificationResolver
from domain.services.income_calculator import IncomeCalculator
from domain.services.volume_calculator import VolumeCalculator

HAMKOR = QUALIFICATIONS[0]


class EveronCalculator:
    """
    Главный фасад: связывает QualificationResolver и IncomeCalculator,
    собирает финальный IncomeResponse для участника.
    """

    def __init__(self):
        self._resolver = QualificationResolver()
        self._income = IncomeCalculator(self._resolver)

    @property
    def volume(self) -> VolumeCalculator:
        return self._resolver.volume

    def calculate(self, member: Member) -> IncomeResponse:
        member_q = self._resolver.qualify(member)
        group_volume = self.volume.group_volume(member)
        yonbosh = self._yonbosh_for_response(member, member_q)

        # Неактивный — все нули
        if member_q is HAMKOR and member.lo < 50:
            return self._zero_response(member, group_volume, yonbosh)

        personal_money, personal_item = self._income.personal(member, member_q)
        team_money, team_items = self._income.team(member, member_q)
        leader_money, leader_items = self._income.leader(member, member_q)

        total = personal_money + team_money + leader_money
        veron = member.lo * member_q.personal_percent

        return IncomeResponse(
            user_id=member.user_id,
            qualification=member_q.name,
            lo=member.lo,
            go=group_volume,
            side_volume=yonbosh,
            points=group_volume,
            personal_bonus=member_q.personal_percent,
            structure_bonus=member_q.team_percent,
            mentor_bonus=member_q.mentor_percent,
            extra_bonus=member_q.extra_bonus,
            personal_money=int(round(personal_money)),
            group_money=int(round(team_money)),
            leader_money=int(round(leader_money)),
            side_vol_money=0,
            total_money=int(round(total)),
            veron=int(round(veron)),
            total_income=float(round(total)),
            branches_info=[],
        )

    def _yonbosh_for_response(self, member, member_q):
        """Yonbosh для отображения — относительно итоговой квалификации."""
        total = member.lo
        for child in member.team:
            child_q = self._resolver.qualify(child)
            if child_q.min_points < member_q.min_points:
                total += child.group_volume()
        return total

    def _zero_response(self, member, group_volume, yonbosh) -> IncomeResponse:
        return IncomeResponse(
            user_id=member.user_id,
            qualification=HAMKOR.name,
            lo=member.lo,
            go=group_volume,
            side_volume=yonbosh,
            points=0,
            personal_bonus=0,
            structure_bonus=0,
            mentor_bonus=0,
            extra_bonus=HAMKOR.extra_bonus,
            personal_money=0,
            group_money=0,
            leader_money=0,
            side_vol_money=0,
            total_money=0,
            veron=0,
            total_income=0.0,
            branches_info=[],
        )
