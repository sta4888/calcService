from domain.models.member import Member, SIDE_VOLUME_THRESHOLD
from domain.services.income_calculator import IncomeCalculator, VERON_PRICE

from domain.value_objects.qualifications import qualification_by_points, QUALIFICATIONS

import pytest

from tests.domain.factories import m


##################################################
######## Тест основной функции calculate #########
##################################################
# region тест метода calculate
@pytest.mark.parametrize("member, expect", [
    (

            m(1, lo=100),
            {
                "user_id": 1,
                "qualification": "Hamkor",  # минимальная квалификация
                "lo": 100,
                "go": 100,
                "side_volume": 100,
                "points": 100,

                # бонусы (проценты)
                "personal_bonus": 0.40,
                "structure_bonus": 0,
                "mentor_bonus": 0,
                "extra_bonus": '-',

                # деньги
                "personal_money": 280_000,
                "group_money": 0,
                "leader_money": 0,
                "total_money": 280_000,
                "veron": 100 * 0.40,
                "total_income": 280_000,

                # ветки
                "branches_info": [],
            }
    ),
    (
            m(1410, lo=1500),
            {
                "user_id": 1410,
                "qualification": "Menejer",  # минимальная квалификация
                "lo": 1500,
                "go": 1500,
                "side_volume": 1500,
                "points": 1500,

                # бонусы (проценты)
                "personal_bonus": 0.40,
                "structure_bonus": 0.35,
                "mentor_bonus": 0.03,
                "extra_bonus": 'Changyutgich',

                # деньги
                "personal_money": 4_200_000,
                "group_money": 3_675_000,
                "leader_money": 0,
                "total_money": 7_875_000,
                "veron": 1500 * 0.40,
                "total_income": 7_875_000,

                # ветки
                "branches_info": [],
            }
    ),
    (
            m(1312, lo=500, team=[
                m(1410, lo=1500),
            ]),
            {
                "user_id": 1312,
                "qualification": "Mentor",  # минимальная квалификация
                "lo": 500,
                "go": 2000,
                "side_volume": 500,
                "points": 500,  # ??????????? вообще ХЗ что это и для чего

                # бонусы (проценты)
                "personal_bonus": 0.40,
                "structure_bonus": 0.2,
                "mentor_bonus": 0.02,
                "extra_bonus": 'Par dazmol',

                # деньги
                "personal_money": 1_400_000,
                "group_money": 700_000,
                "leader_money": 210_000,
                "total_money": 2_310_000,
                "veron": 500 * 0.40,
                "total_income": 2_310_000,

                # ветки
                "branches_info": [],
            }
    ),
    (
            m(1101, lo=450, team=[
                m(1210, lo=2000),
                m(1212, lo=500),
                m(1213, lo=500, team=[
                    m(1310, lo=500),
                    m(1311, lo=500),
                    m(1312, lo=500, team=[
                        m(1410, lo=1500)
                    ]),
                ]),
                m(1211, lo=50, team=[
                    m(1301, lo=500),
                    m(1300, lo=200, team=[
                        m(1400, lo=500),
                        m(1401, lo=500),
                        m(1402, lo=300)
                    ])
                ])
            ]),
            {
                "user_id": 1101,
                "qualification": "Direktor",  # минимальная квалификация
                "lo": 450,
                "go": 8500,
                "side_volume": 500,
                "points": 8500,  # ??????????? вообще ХЗ что это и для чего

                # бонусы (проценты)
                "personal_bonus": 0.40,
                "structure_bonus": 0.45,
                "mentor_bonus": 0.04,
                "extra_bonus": 'Televizor smart-32',

                # деньги
                "personal_money": 1_260_000,
                "group_money": 4_200_000,
                "leader_money": 980_000,
                "total_money": 8_015_000,
                "veron": 450 * 0.40,
                "total_income": 8_015_000,

                # ветки
                "branches_info": [],
            }
    ),
    (
            m(1000, lo=100, team=[
                m(1100, lo=100, team=[
                    m(1200, lo=1000),
                    m(1201, lo=1000),
                    m(1202, lo=1000),
                ]),
                m(1101, lo=450, team=[
                    m(1210, lo=2000),
                    m(1212, lo=500),
                    m(1213, lo=500, team=[
                        m(1310, lo=500),
                        m(1311, lo=500),
                        m(1312, lo=500, team=[
                            m(1410, lo=1500)  # допустим >= SIDE_VOLUME_THRESHOLD
                        ]),
                    ]),
                    m(1211, lo=50, team=[
                        m(1301, lo=500),
                        m(1300, lo=200, team=[
                            m(1400, lo=500),
                            m(1401, lo=500),
                            m(1402, lo=300)
                        ])
                    ])
                ]),
                m(1102, lo=100, team=[]),
                m(1103, lo=100, team=[]),
                m(1104, lo=1000, team=[]),
                m(1105, lo=100, team=[]),
            ]),
            {
                "user_id": 1000,
                "qualification": "Bronza",  # минимальная квалификация
                "lo": 100,
                "go": 13000,
                "side_volume": 500,
                "points": 13000,  # ??????????? вообще ХЗ что это и для чего

                # бонусы (проценты)
                "personal_bonus": 0.40,
                "structure_bonus": 0.55,
                "mentor_bonus": 0.05,
                "extra_bonus": 'Gaz plita',

                # деньги
                "personal_money": 280_000,
                "group_money": 15750000,
                "leader_money": 0,
                "total_money": 17_955_000,
                "veron": 100 * 0.40,
                "total_income": 17_955_000,

                # ветки
                "branches_info": [],
            }
    ),
    (
            m(1200, lo=1000),
            {
                "user_id": 1200,
                "qualification": "Mentor",  # минимальная квалификация
                "lo": 1000,
                "go": 1000,
                "side_volume": 1000,
                "points": 1000,  # ??????????? вообще ХЗ что это и для чего

                # бонусы (проценты)
                "personal_bonus": 0.40,
                "structure_bonus": 0.2,
                "mentor_bonus": 0.02,
                "extra_bonus": 'Par dazmol',

                # деньги
                "personal_money": 2_800_000,
                "group_money": 1_400_000,
                "leader_money": 0,
                "total_money": 4_200_000,
                "veron": 1000 * 0.40,
                "total_income": 4_200_000,

                # ветки
                "branches_info": [],
            }
    ),
])
def test_calculate_smoke(member, expect):
    calc = IncomeCalculator()

    response, breakdown = calc.calculate(member)

    # идентификаторы и объемы
    assert response.user_id == expect["user_id"]
    assert response.qualification == expect["qualification"]
    assert response.lo == expect["lo"]
    assert response.go == expect["go"]
    assert response.side_volume == expect["side_volume"]
    assert response.points == expect["points"]

    # бонусы
    assert response.personal_bonus == expect["personal_bonus"]
    assert response.structure_bonus == expect["structure_bonus"]
    assert response.mentor_bonus == expect["mentor_bonus"]
    assert response.extra_bonus == expect["extra_bonus"]

    # деньги
    assert response.personal_money == expect["personal_money"]
    assert response.group_money == expect["group_money"]
    assert response.leader_money == expect["leader_money"]
    assert response.total_money == expect["total_money"]
    assert response.veron == expect["veron"]
    assert response.total_income == expect["total_income"]

    # ветки
    # assert response.branches_info == expect["branches_info"]


# endregion
# fixme не корректный расчет данных о group_money

# для того чтоб протестировать нам этот метод полностью, нам нужно протестировать методы что внутри
# для этого нужно протестировать всего несколько методов по отдельности

##################################################
######## Тест общего ГО участника ################
##################################################
# region тест ГО участника ✅
@pytest.mark.parametrize("member, expect", [
    (

            m(1, lo=100),
            100
    ),
    (
            m(1410, lo=1500),
            1500
    ),
    (
            m(1312, lo=500, team=[
                m(1410, lo=1500),
            ]),
            2000
    ),
    (
            m(1101, lo=450, team=[
                m(1210, lo=2000),
                m(1212, lo=500),
                m(1213, lo=500, team=[
                    m(1310, lo=500),
                    m(1311, lo=500),
                    m(1312, lo=500, team=[
                        m(1410, lo=1500)
                    ]),
                ]),
                m(1211, lo=50, team=[
                    m(1301, lo=500),
                    m(1300, lo=200, team=[
                        m(1400, lo=500),
                        m(1401, lo=500),
                        m(1402, lo=300)
                    ])
                ])
            ]),
            8500
    ),
    (
            m(1000, lo=100, team=[
                m(1100, lo=100, team=[
                    m(1200, lo=1000),
                    m(1201, lo=1000),
                    m(1202, lo=1000),
                ]),
                m(1101, lo=450, team=[
                    m(1210, lo=2000),
                    m(1212, lo=500),
                    m(1213, lo=500, team=[
                        m(1310, lo=500),
                        m(1311, lo=500),
                        m(1312, lo=500, team=[
                            m(1410, lo=1500)  # допустим >= SIDE_VOLUME_THRESHOLD
                        ]),
                    ]),
                    m(1211, lo=50, team=[
                        m(1301, lo=500),
                        m(1300, lo=200, team=[
                            m(1400, lo=500),
                            m(1401, lo=500),
                            m(1402, lo=300)
                        ])
                    ])
                ]),
                m(1102, lo=100, team=[]),
                m(1103, lo=100, team=[]),
                m(1104, lo=1000, team=[]),
                m(1105, lo=100, team=[]),
            ]),
            13000
    ),
])
def test_group_volume(member, expect):
    assert member.group_volume() == expect


# endregion

##################################################
######## Тест проверки квалификации по ГО ########
##################################################
# region тест проверки квалификации по ГО ✅
@pytest.mark.parametrize("member, expect", [
    (

            m(1, lo=100),
            0
    ),
    (
            m(1410, lo=1500),
            2
    ),
    (
            m(1312, lo=500, team=[
                m(1410, lo=1500),
            ]),
            2
    ),
    (
            m(1101, lo=450, team=[
                m(1210, lo=2000),
                m(1212, lo=500),
                m(1213, lo=500, team=[
                    m(1310, lo=500),
                    m(1311, lo=500),
                    m(1312, lo=500, team=[
                        m(1410, lo=1500)
                    ]),
                ]),
                m(1211, lo=50, team=[
                    m(1301, lo=500),
                    m(1300, lo=200, team=[
                        m(1400, lo=500),
                        m(1401, lo=500),
                        m(1402, lo=300)
                    ])
                ])
            ]),
            3
    ),
    (
            m(1000, lo=100, team=[
                m(1100, lo=100, team=[
                    m(1200, lo=1000),
                    m(1201, lo=1000),
                    m(1202, lo=1000),
                ]),
                m(1101, lo=450, team=[
                    m(1210, lo=2000),
                    m(1212, lo=500),
                    m(1213, lo=500, team=[
                        m(1310, lo=500),
                        m(1311, lo=500),
                        m(1312, lo=500, team=[
                            m(1410, lo=1500)  # допустим >= SIDE_VOLUME_THRESHOLD
                        ]),
                    ]),
                    m(1211, lo=50, team=[
                        m(1301, lo=500),
                        m(1300, lo=200, team=[
                            m(1400, lo=500),
                            m(1401, lo=500),
                            m(1402, lo=300)
                        ])
                    ])
                ]),
                m(1102, lo=100, team=[]),
                m(1103, lo=100, team=[]),
                m(1104, lo=1000, team=[]),
                m(1105, lo=100, team=[]),
            ]),
            4
    ),
])
def test_qualification_by_points(member, expect):
    group_volume = member.group_volume()
    assert qualification_by_points(int(group_volume)) == QUALIFICATIONS[expect]


# endregion


##################################################
######## Тест проверки бокового объема ###########
##################################################
# region тест проверки бокового объема ✅
@pytest.mark.parametrize("member, expect", [
    (

            m(1, lo=100),
            100
    ),
    (
            m(1410, lo=1500),
            1500
    ),
    (
            m(1312, lo=500, team=[
                m(1410, lo=1500),
            ]),
            500
    ),
    (
            m(1101, lo=450, team=[
                m(1210, lo=2000),
                m(1212, lo=500),
                m(1213, lo=500, team=[
                    m(1310, lo=500),
                    m(1311, lo=500),
                    m(1312, lo=500, team=[
                        m(1410, lo=1500)
                    ]),
                ]),
                m(1211, lo=50, team=[
                    m(1301, lo=500),
                    m(1300, lo=200, team=[
                        m(1400, lo=500),
                        m(1401, lo=500),
                        m(1402, lo=300)
                    ])
                ])
            ]),
            500
    ),
    (
            m(1000, lo=100, team=[
                m(1100, lo=100, team=[
                    m(1200, lo=1000),
                    m(1201, lo=1000),
                    m(1202, lo=1000),
                ]),
                m(1101, lo=450, team=[
                    m(1210, lo=2000),
                    m(1212, lo=500),
                    m(1213, lo=500, team=[
                        m(1310, lo=500),
                        m(1311, lo=500),
                        m(1312, lo=500, team=[
                            m(1410, lo=1500)  # допустим >= SIDE_VOLUME_THRESHOLD
                        ]),
                    ]),
                    m(1211, lo=50, team=[
                        m(1301, lo=500),
                        m(1300, lo=200, team=[
                            m(1400, lo=500),
                            m(1401, lo=500),
                            m(1402, lo=300)
                        ])
                    ])
                ]),
                m(1102, lo=100, team=[]),
                m(1103, lo=100, team=[]),
                m(1104, lo=1000, team=[]),
                m(1105, lo=100, team=[]),
            ]),
            500
    ),
])
def test_side_volume(member, expect):
    calc = IncomeCalculator()
    group_volume = member.group_volume()
    base_qualification = qualification_by_points(int(group_volume))
    assert calc.calculate_side_volume(member, base_qualification) == expect


# endregion

#############################################################
######## Тест проверки определенности квалификации ##########
#############################################################
# region тест проверки определенности квалификации ❓
@pytest.mark.parametrize("member, expect", [
    (
            m(1, lo=100),
            {"points": 100, "qualification": qualification_by_points(100)}
    ),
    (
            m(1410, lo=1500),
            {"points": 1500, "qualification": qualification_by_points(1500)}
    ),
    (
            m(1312, lo=500, team=[
                m(1410, lo=1500),
            ]),
            {"points": 500, "qualification": qualification_by_points(500)}
    ),
    (
            m(1101, lo=450, team=[
                m(1210, lo=2000),
                m(1212, lo=500),
                m(1213, lo=500, team=[
                    m(1310, lo=500),
                    m(1311, lo=500),
                    m(1312, lo=500, team=[
                        m(1410, lo=1500)
                    ]),
                ]),
                m(1211, lo=50, team=[
                    m(1301, lo=500),
                    m(1300, lo=200, team=[
                        m(1400, lo=500),
                        m(1401, lo=500),
                        m(1402, lo=300)
                    ])
                ])
            ]),
            {"points": 8500, "qualification": qualification_by_points(8500)}
    ),
    (
            m(1000, lo=100, team=[
                m(1100, lo=100, team=[
                    m(1200, lo=1000),
                    m(1201, lo=1000),
                    m(1202, lo=1000),
                ]),
                m(1101, lo=450, team=[
                    m(1210, lo=2000),
                    m(1212, lo=500),
                    m(1213, lo=500, team=[
                        m(1310, lo=500),
                        m(1311, lo=500),
                        m(1312, lo=500, team=[
                            m(1410, lo=1500)
                        ]),
                    ]),
                    m(1211, lo=50, team=[
                        m(1301, lo=500),
                        m(1300, lo=200, team=[
                            m(1400, lo=500),
                            m(1401, lo=500),
                            m(1402, lo=300)
                        ])
                    ])
                ]),
                m(1102, lo=100, team=[]),
                m(1103, lo=100, team=[]),
                m(1104, lo=1000, team=[]),
                m(1105, lo=100, team=[]),
            ]),
            {
                "points": 13000,
                "qualification": qualification_by_points(13000)
            }
    ),
])
def test_determine_qualification(member, expect):
    calc = IncomeCalculator()

    group_volume = member.group_volume()
    base_qualification = qualification_by_points(int(group_volume))
    side_volume = calc.calculate_side_volume(member, base_qualification)

    qualification, points = calc._determine_qualification(
        member,
        group_volume,
        side_volume,
    )

    assert points == expect["points"]
    assert qualification == expect["qualification"]


# endregion


#############################################################
######## Тест расчета денежных средств #####################
#############################################################
# region тест расчета денежных средств ❓

def test_calculate_money(member, expect):
    calc = IncomeCalculator()
    group_volume = member.group_volume()
    base_qualification = qualification_by_points(int(group_volume))
    side_volume = calc.calculate_side_volume(member, base_qualification)

    qualification, points = calc._determine_qualification(
        member,
        group_volume,
        side_volume,
    )

    money, branches_info, breakdown = calc._calculate_money(member, qualification, side_volume)

# ############################################################
# ######################## СТАРЫЕ ТЕСТЫ ######################
# ############################################################
# region СТАРЫЕ ТЕСТЫ
# @pytest.mark.parametrize(
#     "side_volume, qualification_points, expect_money",
#     [
#         (0, 0, 0),
#         (100, 0, 0),  # Hamkor
#         (500, 500, 500 * 0.20 * VERON_PRICE),  # Mentor
#         (1500, 1500, 1500 * 0.35 * VERON_PRICE),  # Menejer
#     ],
# )
# def test_side_volume_income(side_volume, qualification_points, expect_money):
#     calc = IncomeCalculator()
#     qualification = qualification_by_points(qualification_points)
#
#     money, items = calc._side_volume_income(side_volume, qualification)
#
#     assert money == expect_money
#
#     if side_volume == 0:
#         assert items == []
#     else:
#         assert len(items) == 1
#         item = items[0]
#
#         assert item.volume == side_volume
#         assert item.percent == qualification.team_percent
#         assert item.money == expect_money
#
#
# @pytest.mark.parametrize(
#     "branch_lo, branch_side, branch_points, parent_points, expect_volume",
#     [
#         # Hamkor → всегда 0
#         (100, 100, 0, 1500, 0),
#
#         # Обычная ветка, side < 500
#         (200, 200, 0, 500, 200),
#
#         # Закрытая ветка → берём lo
#         (300, 800, 500, 1500, 300),
#     ],
# )
# def test_income_from_plain_branch(
#         branch_lo,
#         branch_side,
#         branch_points,
#         parent_points,
#         expect_volume,
# ):
#     calc = IncomeCalculator()
#
#     branch = m(1, lo=branch_lo)
#     parent_q = qualification_by_points(parent_points)
#     branch_q = qualification_by_points(branch_points)
#
#     money, items = calc._income_from_plain_branch(
#         branch=branch,
#         branch_side=branch_side,
#         branch_q=branch_q,
#         parent_qualification=parent_q,
#     )
#
#     if expect_volume == 0:
#         assert money == 0
#         assert items == []
#         return
#
#     percent = parent_q.team_percent - branch_q.team_percent
#     expect_money = expect_volume * percent * VERON_PRICE
#
#     assert money == expect_money
#     assert len(items) == 1
#     assert items[0].volume == expect_volume
#     assert items[0].percent == percent
#
#
# def test_analyze_branches_smoke():
#     """
#     Базовый smoke:
#     1 родитель
#     1 слабая ветка
#     """
#     member = m(
#         1,
#         lo=500,
#         team=[
#             m(2, lo=200),
#         ],
#     )
#
#     calc = IncomeCalculator()
#     parent_q = qualification_by_points(500)
#     parent_side = 500
#
#     total_money, branches_info, breakdown = calc._analyze_branches(
#         member=member,
#         parent_qualification=parent_q,
#         parent_side_volume=parent_side,
#     )
#
#     assert total_money > 0
#     assert isinstance(breakdown, list)
#     assert branches_info == []
#
#
# ############################################################
# ######################## СТАРЫЕ ТЕСТЫ ######################
# ############################################################
#
# @pytest.mark.skip(reason="This test is currently good")
# @pytest.mark.parametrize(
#     "branch, expected",
#     [
#         # 1. Только LO
#         (
#                 m(1, lo=100),
#                 100
#         ),
#
#         # 2. Один ребенок Hamkor (учитывается)
#         (
#                 m(1, lo=100, team=[
#                     m(2, lo=200)
#                 ]),
#                 300
#         ),
#
#         # 3. Ребенок закрыт (SV >= threshold и не Hamkor)
#         (
#                 m(1, lo=100, team=[
#                     m(2, lo=600)  # допустим >= SIDE_VOLUME_THRESHOLD
#                 ]),
#                 100
#         ),
#
#         # 4. Глубокая рекурсия
#         (
#                 m(1, lo=100, team=[
#                     m(2, lo=200, team=[
#                         m(3, lo=150)
#                     ])
#                 ]),
#                 450
#         ),
#         # 5 тест проверки с реальными данными
#         (
#                 m(1410, lo=1500),
#                 1500
#         ),
#         # 6 тест проверки с реальными данными
#         (
#                 m(1312, lo=500, team=[
#                     m(1410, lo=1500)  # допустим >= SIDE_VOLUME_THRESHOLD
#                 ]),
#                 500
#         ),
#         # 7 тест проверки с реальными данными Direktor 1
#         (
#                 m(1213, lo=500, team=[
#                     m(1310, lo=500),
#                     m(1311, lo=500),
#                     m(1312, lo=500, team=[
#                         m(1410, lo=1500)  # допустим >= SIDE_VOLUME_THRESHOLD
#                     ]),
#                 ]),
#                 500
#         ),
#         # 8 тест проверки с реальными данными Direktor 2
#         (
#                 m(1101, lo=450, team=[
#                     m(1210, lo=2000),
#                     m(1212, lo=500),
#                     m(1213, lo=500, team=[
#                         m(1310, lo=500),
#                         m(1311, lo=500),
#                         m(1312, lo=500, team=[
#                             m(1410, lo=1500)  # допустим >= SIDE_VOLUME_THRESHOLD
#                         ]),
#                     ]),
#                     m(1211, lo=50, team=[
#                         m(1301, lo=500),
#                         m(1300, lo=200, team=[
#                             m(1400, lo=500),
#                             m(1401, lo=500),
#                             m(1402, lo=300)
#                         ])
#                     ])
#                 ]),
#                 500
#         ),
#         (
#                 m(1000, lo=100, team=[
#                     m(1100, lo=100, team=[
#                         m(1200, lo=1000),
#                         m(1201, lo=1000),
#                         m(1202, lo=1000),
#                     ]),
#                     m(1101, lo=450, team=[
#                         m(1210, lo=2000),
#                         m(1212, lo=500),
#                         m(1213, lo=500, team=[
#                             m(1310, lo=500),
#                             m(1311, lo=500),
#                             m(1312, lo=500, team=[
#                                 m(1410, lo=1500)  # допустим >= SIDE_VOLUME_THRESHOLD
#                             ]),
#                         ]),
#                         m(1211, lo=50, team=[
#                             m(1301, lo=500),
#                             m(1300, lo=200, team=[
#                                 m(1400, lo=500),
#                                 m(1401, lo=500),
#                                 m(1402, lo=300)
#                             ])
#                         ])
#                     ]),
#                     m(1102, lo=100, team=[]),
#                     m(1103, lo=100, team=[]),
#                     m(1104, lo=1000, team=[]),
#                     m(1105, lo=100, team=[]),
#                 ]),
#                 500
#         ),
#     ]
# )
# def test_branch_side(branch, expected):
#     calc = IncomeCalculator()
#     assert calc._branch_side(branch) == expected
#
#
# @pytest.mark.parametrize(
#     "member, parent_q_points, expected_go",
#     [
#         # 1. Нет сильных веток
#         (
#                 m(1, lo=0, team=[
#                     m(2, lo=100),
#                     m(3, lo=150),
#                 ]),
#                 500,
#                 0
#         ),
#
#         # 2. Одна сильная ветка
#         (
#                 m(1, lo=0, team=[
#                     m(2, lo=600),
#                     m(3, lo=100),
#                 ]),
#                 500,
#                 600
#         ),
#
#         # 3. Две сильные ветки
#         (
#                 m(1, lo=0, team=[
#                     m(2, lo=600),
#                     m(3, lo=700),
#                 ]),
#                 500,
#                 1300
#         ),
#     ]
# )
# def test_strong_branches_go(member, parent_q_points, expected_go):
#     calc = IncomeCalculator()
#     parent_q = qualification_by_points(parent_q_points)
#
#     assert calc._strong_branches_go(member, parent_q) == expected_go
#
#
# @pytest.mark.parametrize(
#     "member, gv, sv, expected_points",
#     [
#         # 1. SV < threshold → берем SV
#         (
#                 m(1, lo=100),
#                 1000,
#                 400,
#                 400
#         ),
#
#         # 2. SV >= threshold и нет сильных веток → берем GV
#         (
#                 m(1, lo=100),
#                 1000,
#                 600,
#                 1000
#         ),
#
#         # 3. Есть сильная ветка → берем SV
#         (
#                 m(1, lo=100, team=[
#                     m(2, lo=700)
#                 ]),
#                 1000,
#                 600,
#                 600
#         ),
#     ]
# )
# def test_determine_qualification(member, gv, sv, expected_points):
#     calc = IncomeCalculator()
#     q, points = calc._determine_qualification(member, gv, sv)
#
#     assert points == expected_points
#
#
# @pytest.mark.parametrize("member, expect", [
#     (Member(user_id=1, lo=100), 100),
#     (Member(user_id=1, lo=100, team=[
#         m(2, lo=600),
#     ]), 700),
#     (Member(
#         user_id=1,
#         lo=100,
#         team=[
#             Member(
#                 user_id=2,
#                 lo=200,
#                 team=[
#                     Member(user_id=5, lo=50),
#                     Member(user_id=6, lo=50),
#                 ]
#             ),
#             Member(
#                 user_id=3,
#                 lo=200,
#                 team=[
#                     Member(user_id=7, lo=50),
#                     Member(user_id=8, lo=50),
#                 ]
#             ),
#             Member(
#                 user_id=4,
#                 lo=200,
#                 team=[
#                     Member(user_id=9, lo=50),
#                     Member(user_id=10, lo=50),
#                 ]
#             ),
#         ]
#     ), 1000),
#     (Member(
#         user_id=1,
#         lo=0,
#         team=[
#             Member(user_id=2, lo=0),
#             Member(user_id=3, lo=0),
#         ]
#     ), 0)
# ])
# def test_group_volume_single_member(member, expect):
#     assert member.group_volume() == expect
#
# @pytest.mark.parametrize("member, expect", [
#     (Member(user_id=1, lo=100), 100),
#     (m(
#         1, lo=100, team=[
#             m(2, lo=50),
#             m(3, lo=50),
#         ]
#     ), 200),
#     (m(
#         1, lo=100, team=[
#             m(2, lo=50, team=[
#                 m(3, lo=25)
#             ])
#         ]
#     ),175),
#     (m(
#         1, lo=100, team=[
#             m(2, lo=600),
#             m(3, lo=50),
#         ]
#     ),150),
# ])
# def test_branch_side_single_member(member, expect):
#     calc = IncomeCalculator()
#     assert calc._branch_side(member) == expect
#
#
# @pytest.mark.parametrize(
#     "parent_lo, branches, parent_points, expected",
#     [
#         (
#             100,
#             [
#                 m(2, lo=600),  # закрыл статус
#                 m(3, lo=300),  # не закрыл
#             ],
#             500,
#             400,
#         ),
#     ]
# )
# def test_side_volume(parent_lo, branches, parent_points, expected):
#     parent = m(1, lo=parent_lo, team=branches)
#     parent_q = qualification_by_points(parent_points)
#
#     calc = IncomeCalculator()
#     assert calc._calculate_side_volume(parent, parent_q) == expected
# endregion
