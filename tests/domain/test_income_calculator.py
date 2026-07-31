# tests/test_everon_calculator.py
# -*- coding: utf-8 -*-
import pytest
from unittest.mock import Mock

from domain.models.member import Member
from domain.services.everon_calculator import EveronCalculator
from domain.services.income_calculator import VERON_PRICE
from domain.value_objects.qualifications import QUALIFICATIONS
from web.scheme.schemas import IncomeResponse


HAMKOR = QUALIFICATIONS[0]
MENTOR = QUALIFICATIONS[1]
MENEJER = QUALIFICATIONS[2]
DIREKTOR = QUALIFICATIONS[3]


def make_member(user_id: int, lo: float, team=None) -> Mock:
    m = Mock(spec=Member)
    m.user_id = user_id
    m.lo = float(lo)
    m.team = team or []
    m.group_volume.side_effect = lambda: m.lo + sum(c.group_volume() for c in m.team)
    return m


def qual_by_name(name: str):
    for q in QUALIFICATIONS:
        if q.name == name:
            return q
    raise KeyError(name)


@pytest.fixture
def calc():
    return EveronCalculator()


# =============================================================================
# HAMKOR — нулевой ответ
# =============================================================================

class TestHamkorResponses:
    """Hamkor → все деньги 0, бонусы 0, points 0, но lo/go/side_volume сохраняются."""

    def test_inactive_lo_below_threshold(self, calc):
        """LO < ACTIVITY_THRESHOLD (50) → совсем неактивный, всё ноль."""
        m = make_member(1, lo=30)
        r = calc.calculate(m)

        assert isinstance(r, IncomeResponse)
        assert r.user_id == 1
        assert r.qualification == HAMKOR.name
        assert r.lo == 30.0
        assert r.go == 30.0
        assert r.side_volume == 30.0
        assert r.points == 0
        assert r.personal_bonus == 0
        assert r.structure_bonus == 0
        assert r.mentor_bonus == 0
        assert r.extra_bonus == HAMKOR.extra_bonus
        assert r.personal_money == 0
        assert r.group_money == 0
        assert r.leader_money == 0
        assert r.side_vol_money == 0
        assert r.total_money == 0
        assert r.veron == 0
        assert r.total_income == 0.0
        assert r.branches_info == []

    def test_active_hamkor_gets_personal_only(self, calc):
        """LO=200, активный, но clean<500 → Hamkor + личный с LO, без team/leader."""
        m = make_member(1, lo=200)
        r = calc.calculate(m)

        expected_personal = int(round(200 * HAMKOR.personal_percent * VERON_PRICE))
        # print(expected_personal)
        expected_veron = int(round(200 * HAMKOR.personal_percent))

        assert r.qualification == HAMKOR.name
        assert r.lo == 200.0
        assert r.go == 200.0
        assert r.side_volume == 200.0
        assert r.points == 200.0                          # clean_go
        assert r.personal_bonus == HAMKOR.personal_percent
        assert r.structure_bonus == HAMKOR.team_percent   # ожидаемо 0
        assert r.mentor_bonus == HAMKOR.mentor_percent    # ожидаемо 0
        assert r.extra_bonus == HAMKOR.extra_bonus
        assert r.personal_money == expected_personal
        assert r.group_money == 0
        assert r.leader_money == 0
        assert r.total_money == expected_personal
        assert r.veron == expected_veron

    def test_hamkor_with_weak_team_still_too_small(self, calc):
        """Родитель + слабый Hamkor-ребёнок, в сумме < 500 → Hamkor."""
        child = make_member(2, lo=100)
        parent = make_member(1, lo=200, team=[child])
        r = calc.calculate(parent)

        assert r.qualification == HAMKOR.name
        assert r.total_money == 560_000
        assert r.go == 300.0
        assert r.side_volume == 300.0  # слабая ветка не отваливается

    def test_lo_exactly_at_threshold(self, calc):
        """LO=50 ровно — активный, но один не вытягивает Mentor."""
        m = make_member(1, lo=50)
        r = calc.calculate(m)
        assert r.qualification == HAMKOR.name

    def test_inactive_parent_with_huge_team_stays_hamkor(self, calc):
        """LO<50 → Hamkor сразу, никакая команда не вытащит."""
        big = make_member(2, lo=5000)   # сам по себе Direktor+
        parent = make_member(1, lo=10, team=[big])
        r = calc.calculate(parent)
        assert r.qualification == HAMKOR.name
        assert r.total_money == 0

        assert r.user_id == 1
        assert r.qualification == HAMKOR.name
        assert r.lo == 10.0
        assert r.go == 5010.0
        assert r.group_side_volume == 10.0
        assert r.side_volume == 10.0
        assert r.points == 0
        assert r.personal_bonus == 0
        assert r.structure_bonus == 0
        assert r.mentor_bonus == 0
        assert r.extra_bonus == HAMKOR.extra_bonus
        assert r.personal_money == 0
        assert r.group_money == 0
        assert r.leader_money == 0
        assert r.side_vol_money == 0
        assert r.total_money == 0
        assert r.veron == 0
        assert r.total_income == 0.0
        assert r.branches_info == []

    def test_may_mistake(self, calc):
        big2 = make_member(2, lo=500)
        big3 = make_member(3, lo=66)
        big4 = make_member(4, lo=81.3)
        big5 = make_member(5, lo=70, team=[big4])
        big6 = make_member(6, lo=100)
        big14 = make_member(14, lo=50)
        big15 = make_member(15, lo=73.3)
        big13 = make_member(13, lo=580)
        big12 = make_member(12, lo=50, team=[big15, big14])
        big11 = make_member(11, lo=60, team=[big13, big12])
        big10 = make_member(10, lo=271.3, team=[big11])
        big9 = make_member(9, lo=666.7, team=[big10])
        big7 = make_member(7, lo=250, team=[big6, big5])
        big8 = make_member(8, lo=72, team=[big9, big7])
        big1 = make_member(1, lo=0, team=[big3, big2, big8])

        r = calc.calculate(big15)

        # # ID 15 #######################################
        assert r.user_id == 15
        assert r.qualification == HAMKOR.name  # menejer
        assert r.lo == 73.3
        assert r.go == 73.3
        assert r.group_side_volume == 73.0  # 621
        assert r.extra_bonus == HAMKOR.extra_bonus
        # #############################################
        r = calc.calculate(big14)
        # # ID 14 #######################################
        assert r.user_id == 14
        assert r.qualification == HAMKOR.name  # menejer
        assert r.lo == 50
        assert r.go == 50
        assert r.group_side_volume == 50  # 621
        assert r.extra_bonus == HAMKOR.extra_bonus
        # #############################################
        r = calc.calculate(big12)
        # # ID 14 #######################################
        assert r.user_id == 12
        assert r.qualification == HAMKOR.name  # menejer
        assert r.lo == 50
        assert r.go == 173.3
        assert r.group_side_volume == 173.0  # 621
        assert r.extra_bonus == HAMKOR.extra_bonus
        # #############################################
        r = calc.calculate(big13)
        # # ID 14 #######################################
        assert r.user_id == 13
        assert r.qualification == MENTOR.name  # menejer
        assert r.lo == 580
        assert r.go == 580
        assert r.group_side_volume == 580  # 621
        assert r.extra_bonus == MENTOR.extra_bonus
        # #############################################
        r = calc.calculate(big11)
        # # ID 14 #######################################
        assert r.user_id == 11
        assert r.qualification == HAMKOR.name  # menejer
        assert r.lo == 60
        assert r.go == 813.3
        assert r.group_side_volume == 813.0  # 621
        assert r.extra_bonus == HAMKOR.extra_bonus
        # #############################################
        r = calc.calculate(big10)
        # # ID 14 #######################################
        assert r.user_id == 10
        assert r.qualification == MENTOR.name  # menejer
        assert r.lo == 271.3
        assert r.go == 1084.6
        assert r.group_side_volume == 1085.0  # 621
        assert r.extra_bonus == MENTOR.extra_bonus
        # #############################################
        r = calc.calculate(big9)
        # # ID 14 #######################################
        assert r.user_id == 9
        assert r.qualification == MENEJER.name  # menejer
        assert r.lo == 666.7
        assert r.go == 1751.3
        assert r.group_side_volume == 1751.0  # 621
        assert r.extra_bonus == MENEJER.extra_bonus
        # #############################################
        r = calc.calculate(big8)
        # # ID 14 #######################################
        assert r.user_id == 8
        assert r.qualification == HAMKOR.name  # menejer
        assert r.lo == 72.0
        assert r.go == 2324.6
        assert r.group_side_volume ==  2325  # 621
        assert r.extra_bonus == HAMKOR.extra_bonus
        # #############################################
        r = calc.calculate(big7)
        # # ID 14 #######################################
        assert r.user_id == 7
        assert r.qualification == MENTOR.name  # menejer
        assert r.lo == 250.0
        assert r.go == 501.3
        assert r.group_side_volume == 501  # 621
        assert r.extra_bonus == MENTOR.extra_bonus
        # #############################################
        r = calc.calculate(big5)
        # # ID 14 #######################################
        assert r.user_id == 5
        assert r.qualification == HAMKOR.name  # menejer
        assert r.lo == 70
        assert r.go == 151.3
        assert r.group_side_volume == 151  # 621
        assert r.extra_bonus == HAMKOR.extra_bonus
        # #############################################




        # ##################################################################
        #
        # # only 27 and 4
        # big46 = make_member(46, lo=0)
        # big42 = make_member(42, lo=0, team=[big46])
        # big20 = make_member(20, lo=0)
        # big19 = make_member(19, lo=0, team=[big20, big42])
        # big17 = make_member(17, lo=0, team=[big19])
        # big51 = make_member(51, lo=0)
        # big45 = make_member(45, lo=0)
        # big21 = make_member(21, lo=0, team=[big51, big45])
        # big69 = make_member(69, lo=0)
        # big66 = make_member(66, lo=500)
        # big31 = make_member(31, lo=0)
        # big27 = make_member(27, lo=1000, team=[big31, big66, big69])
        # big22 = make_member(22, lo=0, team=[big27])
        # big43 = make_member(43, lo=0)
        # big65 = make_member(65, lo=0)
        # big64 = make_member(64, lo=0, team=[big65])
        # big63 = make_member(63, lo=0)
        # big62 = make_member(62, lo=0, team=[big63, big64])
        #
        # big4 = make_member(4, lo=1000, team=[big17, big21, big22, big43, big62])
        # r = calc.calculate(big27)
        #
        # # ID 27 #######################################
        # assert r.user_id == 27
        # assert r.qualification == MENEJER.name  # menejer
        # assert r.lo == 1000
        # assert r.go == 1500
        # assert r.group_side_volume == 1500  # 621
        # assert r.side_volume == 1000  #
        # assert r.points == 1000
        # assert r.personal_bonus == 0.40
        # assert r.structure_bonus == 0.35
        # assert r.mentor_bonus == 0.03
        # assert r.extra_bonus == MENEJER.extra_bonus
        # assert r.personal_money == 2800000  #
        # assert r.group_money == 2975000  # 4_762_450
        # assert r.leader_money == 0
        # assert r.side_vol_money == 0
        # assert r.total_money == 5775000
        # assert r.veron == 400
        # assert r.total_income == 5775000
        # assert r.branches_info == []
        # #############################################
        #
        # r = calc.calculate(big4)
        # # ID 4 #######################################
        # assert r.user_id == 4
        # assert r.qualification == MENTOR.name  # menejer
        # assert r.lo == 1000
        # assert r.go == 2500
        # assert r.group_side_volume == 2500  # 621
        # assert r.side_volume == 1000  #
        # assert r.points == 1000
        # assert r.personal_bonus == 0.40
        # assert r.structure_bonus == 0.2
        # assert r.mentor_bonus == 0.02
        # assert r.extra_bonus == MENTOR.extra_bonus
        # assert r.personal_money == 2800000  #
        # assert r.group_money == 1400000  # 4_762_450
        # assert r.leader_money == 0
        # assert r.side_vol_money == 0
        # assert r.total_money == 4200000
        # assert r.veron == 400
        # assert r.total_income == 4200000
        # assert r.branches_info == []
        # #############################################
        # ##################################################################


