from app.domain.models.member import Member
from app.domain.value_objects.levels import LEVELS

def get_level(volume: float) -> float:
    level = 0
    for threshold, percent in LEVELS:
        if volume >= threshold:
            level = percent
    return level


def calc_income(root: Member):
    # тут весь код из твоей функции calc_income()
    ...
