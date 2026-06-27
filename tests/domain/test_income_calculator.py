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
        big18 = make_member(18, lo=0)
        big37 = make_member(37, lo=0)
        big53 = make_member(53, lo=100)
        big58 = make_member(58, lo=80)
        big50 = make_member(50, lo=0)
        big49 = make_member(49, lo=0)
        big56 = make_member(56, lo=163)
        big55 = make_member(55, lo=1500)
        big57 = make_member(57, lo=0)
        big59 = make_member(59, lo=107)
        big54 = make_member(54, lo=514, team=[big55, big57, big59])
        big36 = make_member(36, lo=610, team=[big56])
        big35 = make_member(35, lo=0, team=[big49])
        big34 = make_member(34, lo=500, team=[big50, big54])
        big13 = make_member(13, lo=420, team=[big34, big35, big36, big58])
        big12 = make_member(12, lo=98, team=[big13, big18, big37, big53])






        # big23 = make_member(23, lo=0)
        # big25 = make_member(25, lo=0)
        # big26 = make_member(26, lo=0)
        # big44 = make_member(44, lo=0)
        # big68 = make_member(68, lo=0)
        # big41 = make_member(41, lo=0)
        # big32 = make_member(32, lo=0, team=[big41])
        # big8 = make_member(8, lo=0, team=[big23,big32,big25,big26,big44,big68])
        #
        # big16 = make_member(16, lo=0)
        # big28 = make_member(28, lo=0)
        # big30 = make_member(30, lo=0)
        # big38 = make_member(38, lo=0)  # сам по себе Direktor+
        # big67 = make_member(67, lo=0)
        # big61 = make_member(67, lo=0)
        # big33 = make_member(33, lo=0)
        # big29 = make_member(29, lo=0, team=[big30])
        # big60 = make_member(60, lo=0, team=[big61])
        # big15 = make_member(15, lo=0, team=[big16, big28, big29])  # сам по себе Direktor+
        # big14 = make_member(14, lo=0, team=[big38, big60, big67])  # сам по себе Direktor+
        # big6 = make_member(6, lo=0, team=[big14, big15, big33])  # сам по себе Direktor+

        # parent = make_member(1, lo=10, team=[big])
        r = calc.calculate(big13)

        assert r.user_id == 13
        assert r.qualification == DIREKTOR.name  # menejer
        assert r.lo == 420
        assert r.go == 3894
        assert r.group_side_volume == 3894  # 621
        assert r.side_volume == 500  #
        assert r.points == 500
        assert r.personal_bonus == 0.4
        assert r.structure_bonus == 0.45
        assert r.mentor_bonus == 0.04
        assert r.extra_bonus == DIREKTOR.extra_bonus
        assert r.personal_money == 1_176_000  #
        assert r.group_money == 5939500 # 4_762_450
        assert r.leader_money == 0
        assert r.side_vol_money == 0
        assert r.total_money == 5938450
        assert r.veron == 168
        assert r.total_income == 5938450
        assert r.branches_info == []

        # assert r.user_id == 54
        # assert r.qualification == MENTOR.name # menejer
        # assert r.lo == 514
        # assert r.go == 2121
        # assert r.group_side_volume == 621 # 621
        # assert r.side_volume == 621 #
        # assert r.points == 621
        # assert r.personal_bonus == 0.4
        # assert r.structure_bonus == 0.2
        # assert r.mentor_bonus == 0.02
        # assert r.extra_bonus == MENTOR.extra_bonus
        # assert r.personal_money == 1_439_200 #
        # assert r.group_money == 869_400 # 869400
        # assert r.leader_money == 210_000
        # assert r.side_vol_money == 0
        # assert r.total_money == 2_518_600
        # assert r.veron == 206
        # assert r.total_income == 2_518_600
        # assert r.branches_info == []



# # =============================================================================
# # Одиночки — без команды
# # =============================================================================
#
# class TestSoloRanks:
#
#     def test_solo_mentor(self, calc):
#         """LO=500 → Mentor. Командный идёт со своего же объёма (без веток)."""
#         m = make_member(1, lo=500)
#         r = calc.calculate(m)
#
#         assert r.qualification == "Mentor"
#         assert r.personal_money == int(round(500 * 0.40 * VERON_PRICE))  # 1_400_000
#         assert r.group_money == int(round(500 * 0.20 * VERON_PRICE))     # 700_000
#         assert r.leader_money == 0
#         assert r.total_money == 2_100_000
#         assert r.veron == int(round(500 * 0.40))                         # 200
#
#     def test_solo_menejer(self, calc):
#         """LO=1500 → Menejer."""
#         menejer = qual_by_name("Menejer")
#         m = make_member(1, lo=1500)
#         r = calc.calculate(m)
#
#         assert r.qualification == "Menejer"
#         expected_personal = int(round(1500 * menejer.personal_percent * VERON_PRICE))
#         expected_team = int(round(1500 * menejer.team_percent * VERON_PRICE))
#         assert r.personal_money == expected_personal
#         assert r.group_money == expected_team
#         assert r.leader_money == 0
#         assert r.total_money == expected_personal + expected_team
#
#     def test_response_carries_bonus_percents(self, calc):
#         """В ответе процентные бонусы = проценты квалификации (для не-Hamkor)."""
#         m = make_member(42, lo=500)
#         r = calc.calculate(m)
#         mentor = qual_by_name("Mentor")
#         assert r.personal_bonus == mentor.personal_percent
#         assert r.structure_bonus == mentor.team_percent
#         assert r.mentor_bonus == mentor.mentor_percent
#         assert r.extra_bonus == mentor.extra_bonus
#
#
# # =============================================================================
# # Команда — слабая (склеивается в чистый ГО родителя)
# # =============================================================================
#
# class TestWeakTeam:
#
#     def test_mentor_built_from_weak_child(self, calc):
#         """parent LO=200 + Hamkor-child LO=300 → parent тащит ребёнка, становится Mentor."""
#         child = make_member(2, lo=300)
#         parent = make_member(1, lo=200, team=[child])
#         r = calc.calculate(parent)
#
#         assert r.qualification == "Mentor"
#         # личный считается строго по LO родителя
#         assert r.personal_money == int(round(200 * 0.40 * VERON_PRICE))   # 560_000
#         # командный — на чистом ГО (200 + 300)
#         assert r.group_money == int(round(500 * 0.20 * VERON_PRICE))      # 700_000
#         assert r.leader_money == 0                                         # ребёнок Hamkor
#         assert r.go == 500.0
#         assert r.side_volume == 500.0
#
#     def test_personal_money_uses_lo_not_go(self, calc):
#         """Личный — только с LO, даже если ГО намного больше."""
#         kids = [make_member(i, lo=200) for i in range(2, 7)]   # 5 × 200 = 1000
#         parent = make_member(1, lo=100, team=kids)
#         r = calc.calculate(parent)
#         assert r.personal_money == int(round(100 * 0.40 * VERON_PRICE))
#
#
# # =============================================================================
# # Команда — сильная (отваливается → лидерский овердайд)
# # =============================================================================
#
# class TestStrongTeam:
#
#     def test_mentor_under_mentor_breaks_away(self, calc):
#         """Дочерний Mentor отваливается: командный без него, появляется лидерский."""
#         child = make_member(2, lo=500)
#         parent = make_member(1, lo=500, team=[child])
#         r = calc.calculate(parent)
#
#         mentor = qual_by_name("Mentor")
#         assert r.qualification == "Mentor"
#         assert r.personal_money == int(round(500 * mentor.personal_percent * VERON_PRICE))
#         # ветка отвалилась — командный только с LO родителя
#         assert r.group_money == int(round(500 * mentor.team_percent * VERON_PRICE))
#         # лидерский = up_value(child) × mentor_percent
#         assert r.leader_money == int(round(500 * mentor.mentor_percent * VERON_PRICE))
#         assert r.go == 1000.0                # полный GO — для показа
#         assert r.side_volume == 500.0        # чистый — без отвалившейся ветки
#     #
#     # def test_menejer_with_strong_mentor_branch(self, calc):
#     #     """Menejer-родитель + Mentor-ребёнок: лидерский идёт по проценту Menejer."""
#     #     menejer = qual_by_name("Menejer")
#     #     child = make_member(2, lo=500)            # Mentor
#     #     parent = make_member(1, lo=1500, team=[child])
#     #     r = calc.calculate(parent)
#     #
#     #     assert r.qualification == "Menejer"
#     #     assert r.personal_money == int(round(1500 * menejer.personal_percent * VERON_PRICE))
#     #     assert r.group_money == int(round(1500 * menejer.team_percent * VERON_PRICE))
#     #     assert r.leader_money == int(round(500 * menejer.mentor_percent * VERON_PRICE))
#     #     assert r.side_volume == 1500.0
#     #     assert r.go == 2000.0
#
#     def test_mixed_team_weak_stays_strong_breaks(self, calc):
#         """Слабая ветка склеивается, сильная отваливается."""
#         mentor = qual_by_name("Mentor")
#         strong = make_member(2, lo=500)   # Mentor — отвалится
#         weak = make_member(3, lo=300)     # Hamkor — останется в clean
#         parent = make_member(1, lo=500, team=[strong, weak])
#         r = calc.calculate(parent)
#
#         # clean_go(parent) = 500 (LO) + 300 (weak) = 800; strong не считается
#         assert r.qualification == "Mentor"
#         assert r.side_volume == 800.0
#         assert r.go == 1300.0
#         assert r.personal_money == int(round(500 * mentor.personal_percent * VERON_PRICE))
#         assert r.group_money == int(round(800 * mentor.team_percent * VERON_PRICE))
#         assert r.leader_money == int(round(500 * mentor.mentor_percent * VERON_PRICE))
#
#
# # =============================================================================
# # Сброс кэша между вызовами
# # =============================================================================
#
# class TestCacheReset:
#     """resolver.clear() обязан вызываться в начале calculate()."""
#
#     def test_two_calls_same_input_same_output(self, calc):
#         r1 = calc.calculate(make_member(1, lo=500))
#         r2 = calc.calculate(make_member(1, lo=500))
#         assert r1.total_money == r2.total_money
#         assert r1.qualification == r2.qualification
#
#     def test_two_calls_different_volumes_different_results(self, calc):
#         """Один и тот же user_id, разный LO → разный результат (кэш не залип)."""
#         r1 = calc.calculate(make_member(1, lo=500))    # Mentor
#         r2 = calc.calculate(make_member(1, lo=1500))   # Menejer
#         assert r1.qualification == "Mentor"
#         assert r2.qualification == "Menejer"
#         assert r1.total_money != r2.total_money
#
#
# # =============================================================================
# # Раскладка полей в IncomeResponse
# # =============================================================================
#
# class TestResponseFields:
#
#     def test_branches_info_always_empty(self, calc):
#         """Текущий фасад не наполняет branches_info."""
#         m = make_member(1, lo=500, team=[make_member(2, lo=300)])
#         r = calc.calculate(m)
#         assert r.branches_info == []
#
#     def test_side_vol_money_always_zero(self, calc):
#         m = make_member(1, lo=500)
#         r = calc.calculate(m)
#         assert r.side_vol_money == 0
#
#     def test_total_income_matches_total_money(self, calc):
#         m = make_member(1, lo=1500)
#         r = calc.calculate(m)
#         assert r.total_income == float(r.total_money)
#
#     # def test_group_side_volume_rounded_int(self, calc):
#     #     m = make_member(1, lo=500)
#     #     r = calc.calculate(m)
#     #     assert isinstance(r.group_side_volume, int)
#     #     assert r.group_side_volume == 500