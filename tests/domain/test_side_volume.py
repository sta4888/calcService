import pytest

from domain.models.member import Member


def test_side_volume_no_team():
    m = Member(1, lo=100)
    assert m.side_volume() == 100


def test_side_volume_single_branch():
    root = Member(1, lo=100)
    root.team = [Member(2, lo=300)]

    assert root.side_volume() == 400


def test_side_volume_two_branches():
    root = Member(1, lo=100)
    a = Member(2, lo=300)
    b = Member(3, lo=200)

    root.team = [a, b]

    # боковой = меньшая ветка
    assert root.side_volume() == 600


@pytest.mark.parametrize(
    "members, expected",
    [
        # вариант 1: три ветви
        (
                [(1, 100), (2, 500), (3, 200), (4, 100)],  # (id, lo)
                400  # ожидаемый side_volume
        ),
        # можно добавить другие варианты
        (
                [(1, 50), (2, 200), (3, 100)],
                350  # пример
        ),
        (
                [(1, 50), (2, 1000), (3, 1000), (4, 1000),(5, 100)],
                150  # пример
        ),
(
                [(1, 100), (2, 1500), (3, 500)],
                100  # пример
        ),
    ]
)
def test_side_volume_parametrize(members, expected):
    # создаём объекты
    objs = {mid: Member(mid, lo=lo) for mid, lo in members}

    # формируем связи
    # для простоты: первый элемент — root, остальные — его команда
    root = objs[members[0][0]]
    root.team = [objs[mid] for mid, _ in members[1:]]

    assert root.side_volume() == expected


def test_side_volume_dynamic_growth():
    root = Member(1, lo=100)
    a = Member(2, lo=200)
    b = Member(3, lo=300)

    root.team = [a, b]
    assert root.side_volume() == 600

    # слабая ветка обгоняет
    a.lo += 200
    assert root.side_volume() == 800
