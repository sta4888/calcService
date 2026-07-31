# -*- coding: utf-8 -*-
from typing import Dict

from domain.models.member import Member
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import QUALIFICATIONS

from domain.services.volume_calculator import VolumeCalculator

ACTIVITY_THRESHOLD = 50
HAMKOR = QUALIFICATIONS[0]
MENTOR = QUALIFICATIONS[1]


class QualificationResolver:
    """
    Квалификация считается СНИЗУ ВВЕРХ по ДИФФЕРЕНЦИАЛЬНОМУ отсечению:

        ветка отваливается от родителя, если её лидер — Mentor+ с рангом
        >= проверяемого ранга (РАВНЫЙ ранг тоже отваливается).
        HAMKOR-ветки не отваливаются никогда.

    Главный примитив — clean_go(member, rank):
        LO члена + поднятый объём (up_value) детей, чьи ветки НЕ отвалились.
    Тот же clean_go служит и базой для денег за ГО.

    Квалификация = НАИМЕНЬШАЯ неподвижная точка (снизу вверх): ранг родителя
    определяется его LO + поднятыми объёмами слабых веток; ветка, чей ранг
    >= ранга родителя, отваливается и не помогает ему подняться. Родитель
    должен «перебить» такую ветку своим объёмом, иначе она уходит в овердайд.

    qualify / up_value мемоизируются по user_id, иначе рекурсия
    qualify → clean_go → up_value → qualify(child) уходит в переэкспоненту.
    """

    def __init__(self):
        self._volume = VolumeCalculator(self)
        self._qual_cache: Dict[int, Qualification] = {}
        self._up_cache: Dict[int, float] = {}

    @property
    def volume(self) -> VolumeCalculator:
        return self._volume

    def clear(self) -> None:
        """Сбросить кэши (вызывать перед расчётом нового дерева)."""
        self._qual_cache.clear()
        self._up_cache.clear()

    # =================================================================
    # КВАЛИФИКАЦИЯ
    # =================================================================

    def qualify(self, member: Member) -> Qualification:
        cached = self._qual_cache.get(member.user_id)
        if cached is not None:
            return cached
        result = self._resolve(member)
        self._qual_cache[member.user_id] = result
        return result

    def _resolve(self, member: Member) -> Qualification:
        if member.lo < ACTIVITY_THRESHOLD:
            return HAMKOR
        for q in reversed(QUALIFICATIONS):
            if self.clean_go(member, q) >= q.min_points:
                return q
        return HAMKOR

    def _rank_for(self, clean: float) -> Qualification:
        for q in reversed(QUALIFICATIONS):
            if clean >= q.min_points:
                return q
        return HAMKOR

    # =================================================================
    # ЧИСТЫЙ GO / ПОДНЯТЫЙ ОБЪЁМ
    # =================================================================

    def clean_go(self, member, rank):
        total = float(member.lo)
        for child in member.team:
            cq = self.qualify(child)
            breaks_away = (
                    cq.min_points >= MENTOR.min_points
                    and cq.min_points >= rank.min_points
            )
            if not breaks_away:
                total += self.clean_go(child, rank)  # рекурсия с ТЕМ ЖЕ rank
        return total

    def up_value(self, member: Member) -> float:
        """
        Чистый GO, который узел поднимает родителю
        = clean_go при СВОЁМ итоговом ранге.
        """
        cached = self._up_cache.get(member.user_id)
        if cached is not None:
            return cached
        value = self.clean_go(member, self.qualify(member))
        self._up_cache[member.user_id] = value
        return value