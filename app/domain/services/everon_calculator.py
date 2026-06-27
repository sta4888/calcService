# -*- coding: utf-8 -*-
from domain.models.member import Member
from domain.value_objects.qualifications import QUALIFICATIONS
from web.scheme.schemas import IncomeResponse
from domain.services.qualification_resolver import (
    QualificationResolver,
    ACTIVITY_THRESHOLD,
)
from domain.services.qualification_resolver import QualificationResolver
from domain.services.income_calculator import IncomeCalculator
from domain.services.volume_calculator import VolumeCalculator

HAMKOR = QUALIFICATIONS[0]
MENTOR = QUALIFICATIONS[1]


class EveronCalculator:
    def __init__(self):
        self._resolver = QualificationResolver()
        self._income = IncomeCalculator(self._resolver)

    @property
    def volume(self):
        return self._resolver.volume

    def calculate(self, member: Member) -> IncomeResponse:
        self._resolver.clear()

        member_q = self._resolver.qualify(member)
        group_volume = self.volume.group_volume(member)
        clean = self._resolver.clean_go(member, member_q)  # база команды
        side = self._resolver.clean_go(member, MENTOR)  # ← НОВОЕ: LO + Hamkor-ветки

        if member.lo < ACTIVITY_THRESHOLD:
            return self._zero_response(member, group_volume, clean, side)

        personal_money, _ = self._income.personal(member, member_q)
        team_money, _ = self._income.team(member, member_q)
        leader_money, _ = self._income.leader(member, member_q)

        group_side = clean if leader_money > 0 else group_volume
        total = personal_money + team_money + leader_money
        veron = member.lo * member_q.personal_percent

        return IncomeResponse(
            user_id=member.user_id,
            qualification=member_q.name,
            lo=member.lo,
            go=group_volume,
            group_side_volume=int(round(group_side)),
            side_volume=side,  # ← было clean
            points=side,  # ← было clean
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

    def _zero_response(self, member, group_volume, clean, side) -> IncomeResponse:
        return IncomeResponse(
            user_id=member.user_id,
            qualification=HAMKOR.name,
            lo=member.lo,
            go=group_volume,
            group_side_volume=int(round(clean)),  # ← НЕ менял
            side_volume=side,  # ← было clean (для Hamkor совпадает)
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