class DomainError(Exception):
    """Базовая доменная ошибка"""


class InvalidVolumeError(DomainError):
    pass


class EmptyStructureError(DomainError):
    pass
