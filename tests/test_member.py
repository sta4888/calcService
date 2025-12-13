# import pytest
# from app.domain.models.member import Member, calc_income  # предполагаемая структура проекта
#
#
# @pytest.mark.skip
# def test_get_level():
#     from app.domain.models.member import get_level
#     assert get_level(0) == 0.0
#     assert get_level(150) == 0.03
#     assert get_level(1200) == 0.15
#
#
# @pytest.mark.skip
# def test_calc_income_simple():
#     root = Member("Root", 300)
#     result = calc_income(root)
#     assert result["ЛО"] == 300
#     assert result["ГО"] == 300
#     assert result["Личный бонус"] == 300 * 0.06  # если уровень 0.06
#     assert result["Структурный бонус"] == 0
#
#
# @pytest.mark.skip
# def test_calc_income_team():
#     root = Member(
#         "Root",
#         300,
#         team=[Member("A", 200), Member("B", 400)]
#     )
#     result = calc_income(root)
#     assert result["ГО"] == 900  # 300 + 200 + 400
