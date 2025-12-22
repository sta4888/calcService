import pytest

from domain.models.member import Member, SIDE_VOLUME_THRESHOLD
from domain.services.income_calculator import IncomeCalculator
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import qualification_by_points


@pytest.mark.parametrize(
    "member_id, lo, expected_side_volume, expected_points",
    [
        (1, 100, 100, 100),
    ]
)
def test_income_no_team(member_id, lo, expected_side_volume, expected_points):
    m = Member(member_id, lo=lo)
    result = IncomeCalculator().calculate(m)

    assert result.side_volume == expected_side_volume
    assert result.points == expected_points
    assert result.total_income > 0


# @pytest.mark.parametrize('lo, points, qualification, expected', [
#     (
#         500, 2000,
#     )
# ])
# def test_income_money_calculator(lo: int, points: int, qualification: Qualification):
#     # m = Member(1, lo=100)
#     result = IncomeCalculator()._calculate_money(lo, points, qualification)
#
#     assert result.get("lo") == 100
#     assert result.get("go") == 100
#     assert result.get("lider_money") == 100
#     assert result.get("total_money") == 100

@pytest.mark.skip(reason="not implemented")
@pytest.mark.parametrize(
    "members, connections, expected_side_volume, expected_points, expected_qualification",
    [
        # вариант 1: два участника, side < threshold
        (
                [(1, 50), (2, 200), (3, 500), (4, 500), (5, 500), (6, 300)],  # (id, lo)
                {1: [2, 3], 2: [4, 5, 6]},  # связи: ключ — root, значения — его команда
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


# def test_mixed_branches_side_volume():
#     """
#     4 ветки:
#     - закрытая
#     - сильнее родителя
#     - нормальная
#     - слабая
#     """
#     member = Member(user_id=1, lo=100)
#
#     closed = Member(user_id=2, lo=500)
#     stronger = Member(user_id=3, lo=1000)
#     normal = Member(user_id=4, lo=300)
#     weak1 = Member(user_id=5, lo=100)
#     weak2 = Member(user_id=6, lo=100)
#     weak3 = Member(user_id=7, lo=100)
#     weak4 = Member(user_id=8, lo=100)
#
#     member.team = [closed, stronger, normal, weak1, weak2, weak3, weak4]
#
#     calc = IncomeCalculator()
#     parent_q = qualification_by_points(int(member.group_volume()))
#
#     side = calc.calculate_side_volume(member, parent_q)
#
#     # side = LO + normal + weak
#     assert side == 100 + 300 + 100
#
# def test_side_volume_complex_branches_case():
#     """
#     Родитель:
#     LO = 100
#
#     Ветки:
#     1) lo=100, gv=3100, side=100, Hamkor (НЕ закрыта)
#     2) lo=450, gv=8500, side=500, Direktor (ЗАКРЫТА)
#     3) lo=100, gv=100, side=100, Hamkor
#     4) lo=100, gv=100, side=100, Hamkor
#     5) lo=1000, gv=1000, side=1000, Menejer (ЗАКРЫТА)
#     6) lo=100, gv=100, side=100, Hamkor
#
#     Ожидание:
#     side = 100 (LO родителя)
#          + 100 + 100 + 100 + 100 = 500
#     """
#
#     parent = Member(1, lo=100)
#
#     # 1
#     b1 = Member(2, lo=100, team=[Member(20, lo=3000)])
#     # 2
#     b2 = Member(3, lo=450, team=[Member(30, lo=8050)])
#     # 3
#     b3 = Member(4, lo=100)
#     # 4
#     b4 = Member(5, lo=100)
#     # 5
#     b5 = Member(6, lo=1000)
#     # 6
#     b6 = Member(7, lo=100)
#
#     parent.team = [b1, b2, b3, b4, b5, b6]
#
#     calc = IncomeCalculator()
#     base_q = qualification_by_points(int(parent.group_volume()))
#
#     side = calc.calculate_side_volume(parent, base_q)
#
#     assert side == 500

