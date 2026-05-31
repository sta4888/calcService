# -*- coding: utf-8 -*-
from domain.models.member import Member
from domain.value_objects.qualifications import QUALIFICATIONS
from web.scheme.schemas import IncomeResponse

from domain.services.qualification_resolver import QualificationResolver
from domain.services.income_calculator import IncomeCalculator
from domain.services.volume_calculator import VolumeCalculator

HAMKOR = QUALIFICATIONS[0]


class EveronCalculator:
    """
    Фасад: связывает QualificationResolver и IncomeCalculator,
    собирает IncomeResponse для участника.
    """

    def __init__(self):
        self._resolver = QualificationResolver()
        self._income = IncomeCalculator(self._resolver)

    @property
    def volume(self) -> VolumeCalculator:
        return self._resolver.volume

    def calculate(self, member: Member) -> IncomeResponse:
        # дерево могло измениться между вызовами — чистим мемоизацию
        self._resolver.clear()

        member_q = self._resolver.qualify(member)
        group_volume = self.volume.group_volume(member)   # полный GO (показ)
        clean = self._resolver.clean_go(member, member_q)  # чистый GO (база)

        if member_q is HAMKOR:
            return self._zero_response(member, group_volume, clean)

        personal_money, _ = self._income.personal(member, member_q)
        team_money, _ = self._income.team(member, member_q)
        leader_money, _ = self._income.leader(member, member_q)

        total = personal_money + team_money + leader_money
        veron = member.lo * member_q.personal_percent

        return IncomeResponse(
            user_id=member.user_id,
            qualification=member_q.name,
            lo=member.lo,
            go=group_volume,
            side_volume=clean,
            points=clean,
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

    def _zero_response(self, member, group_volume, clean) -> IncomeResponse:
        return IncomeResponse(
            user_id=member.user_id,
            qualification=HAMKOR.name,
            lo=member.lo,
            go=group_volume,
            side_volume=clean,
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