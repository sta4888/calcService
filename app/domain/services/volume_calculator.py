# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

from domain.models.member import Member
from domain.value_objects.qualification import Qualification

if TYPE_CHECKING:
    from domain.services.qualification_resolver import QualificationResolver


class VolumeCalculator:
    """
    Тонкая обёртка над объёмами.
    Вся логика отсечения теперь живёт в QualificationResolver (clean_go),
    потому что она завязана на qulify. Здесь — только то, что нужно
    для отображения.
    """

    def __init__(self, resolver: "QualificationResolver"):
        self._resolver = resolver

    def group_volume(self, member: Member) -> float:
        """Полный GO ветки (сумма всех LO в поддереве) — как есть, для показа."""
        return member.group_volume()

    def clean_go(self, member: Member, rank: Qualification) -> float:
        """Чистый GO относительно ранга (делегирует в resolver)."""
        return self._resolver.clean_go(member, rank)

    def yonbosh(self, member: Member) -> float:
        """
        Чистый боковой для отображения = clean_go при итоговом ранге члена
        (то же, что узел поднял бы наверх).
        """
        return self._resolver.up_value(member)