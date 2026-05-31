# -*- coding: utf-8 -*-
from domain.models.member import Member
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import QUALIFICATIONS

from domain.services.volume_calculator import VolumeCalculator

ACTIVITY_THRESHOLD = 50
SIDE_VOLUME_THRESHOLD = 500
HAMKOR = QUALIFICATIONS[0]


class QualificationResolver:
    """
    Определяет финальную квалификацию участника.

    Алгоритм:
    1. LO < 50 → Hamkor.
    2. По полному GO определяем потенциальную q_pot.
    3. Считаем clean_go (без сильных веток) и yonbosh (LO + Hamkor-ветки).
    4. Если родитель сам закрывает q_pot (clean_go >= q_pot.min_points
       и yonbosh >= 500) → q_pot. Иначе ищем максимальную Q.
    """

    def __init__(self):
        self._volume = VolumeCalculator(self)

    @property
    def volume(self) -> VolumeCalculator:
        return self._volume

    def qualify(self, member: Member) -> Qualification:
        if not self._is_active(member):
            return HAMKOR

        if self._volume.yonbosh(member) < SIDE_VOLUME_THRESHOLD:
            return HAMKOR

        for q in reversed(QUALIFICATIONS):  # от высшего к низшему
            if q is HAMKOR:
                continue
            if self._volume.clean_go(member, q) >= q.min_points:
                return q

        return HAMKOR

    def _is_active(self, member: Member) -> bool:
        return member.lo >= ACTIVITY_THRESHOLD

    def _potential(self, group_volume: float) -> Qualification:
        for q in reversed(QUALIFICATIONS):
            if group_volume >= q.min_points:
                return q
        return HAMKOR
