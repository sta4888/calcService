from domain.services.income_calculator import IncomeCalculator

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
    (
            m(1213, lo=500, team=[
                m(1310, lo=500),
                m(1311, lo=500),
                m(1312, lo=500, team=[
                    m(1410, lo=1500)  # допустим >= SIDE_VOLUME_THRESHOLD
                ]),
            ]),
            {
                "user_id": 1213,
                "qualification": "Direktor",  # минимальная квалификация
                "lo": 500,
                "go": 3500,
                "side_volume": 500,
                "points": 3500,  # ??????????? вообще ХЗ что это и для чего

                # бонусы (проценты)
                "personal_bonus": 0.40,
                "structure_bonus": 0.45,
                "mentor_bonus": 0.04,
                "extra_bonus": 'Televizor smart-32',

                # деньги
                "personal_money": 1_400_000,
                "group_money": 2_625_000 + 1_050_000,
                "leader_money": 0,
                "total_money": 6_650_000,
                "veron": 500 * 0.40,
                "total_income": 6_650_000,

                # ветки
                "branches_info": [],
            }
    ),
    (
            m(1210, lo=2000),
            {
                "user_id": 1210,
                "qualification": "Menejer",  # минимальная квалификация
                "lo": 2000,
                "go": 2000,
                "side_volume": 2000,
                "points": 2000,

                # бонусы (проценты)
                "personal_bonus": 0.40,
                "structure_bonus": 0.35,
                "mentor_bonus": 0.03,
                "extra_bonus": 'Changyutgich',

                # деньги
                "personal_money": 5600000,
                "group_money": 4900000,
                "leader_money": 0,
                "total_money": 10500000,
                "veron": 2000 * 0.40,
                "total_income": 10500000,

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
# endregion
