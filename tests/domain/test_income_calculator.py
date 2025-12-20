import pytest

from domain.models.member import Member, SIDE_VOLUME_THRESHOLD
from domain.services.income_calculator import IncomeCalculator


def test_income_no_team():
    m = Member(1, lo=100)
    result = IncomeCalculator().calculate(m)

    assert result.side_volume == 100
    assert result.points == 100
    assert result.total_income > 0


@pytest.mark.parametrize(
    "members, connections, expected_side_volume, expected_points, expected_qualification",
    [
        # вариант 1: два участника, side < threshold
        (
                [(1, 50), (2, 200), (3, 500), (4, 500), (5, 500), (6, 300)],  # (id, lo)
                {1: [2, 3], 2:[4,5,6]},  # связи: ключ — root, значения — его команда
                50,  # ожидаемый side_volume
                50,  # ожидаемые points
                "Hamkor"  # ожидаемые qualification
        ),
        # вариант 2: другой пример
        # (
        #         [(1, 50), (2, 30), (3, 20)],
        #         {1: [2, 3]},
        #         50,  # пример
        #         50  # пример
        # ),
    ]
)
def test_income_side_volume_parametrize(members, connections, expected_side_volume, expected_points,
                                        expected_qualification):
    # создаём объекты
    objs = {mid: Member(mid, lo=lo) for mid, lo in members}

    # формируем связи
    for parent_id, children_ids in connections.items():
        objs[parent_id].team = [objs[cid] for cid in children_ids]

    root = objs[members[0][0]]
    result = IncomeCalculator().calculate(root)

    assert result.side_volume == expected_side_volume
    assert result.points == expected_points
    assert result.qualification == expected_qualification

# def test_income_side_volume_enough():
#     root = Member(1, lo=100)
#     root.team = [
#         Member(2, lo=600),
#         Member(3, lo=500),
#     ]
#
#     result = IncomeCalculator().calculate(root)
#
#     assert result.side_volume <= SIDE_VOLUME_THRESHOLD
#     assert result.points == int(root.group_volume())
#
#
# def test_income_grows_after_side_threshold():
#     root = Member(1, lo=100)
#     a = Member(2, lo=600)
#     b = Member(3, lo=100)
#
#     root.team = [a, b]
#
#     calc = IncomeCalculator()
#     income_before = calc.calculate(root).total_income
#
#     # добиваем слабую ветку до порога
#     b.lo += 500
#
#     income_after = calc.calculate(root).total_income
#
#     assert income_after > income_before
