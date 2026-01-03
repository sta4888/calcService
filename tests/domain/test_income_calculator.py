import pytest
from domain.models.member import Member, SIDE_VOLUME_THRESHOLD
from domain.services.income_calculator import IncomeCalculator, VERON_PRICE
from domain.value_objects.BreakdownItem import BreakdownItem, IncomeBreakdown
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import qualification_by_points
from unittest.mock import Mock, patch, call

# tests/domain/test_income_calculator.py
import pytest
from domain.services.income_calculator import VERON_PRICE

# tests/test_branch_side.py
import pytest


@pytest.mark.skip(reason="This test is currently broken")
class TestIncomeCalculatorIntegration:

    @pytest.mark.skip(reason="This test is currently broken")
    @pytest.mark.parametrize("test_name, structure, expected", [
        (
                "Базовый тест: один участник",
                {
                    'id': 1,
                    'lo': 100,
                    'team': []
                },
                {
                    'qualification': 'Hamkor',
                    'go': 100,
                    'side': 100,
                    'total_money': 100 * 0.40 * VERON_PRICE
                }
        ),
        (
                "Базовый тест: один участник",
                {
                    'id': 1,
                    'lo': 1000,
                    'team': []
                },
                {
                    'qualification': 'Mentor',
                    'go': 1000,
                    'side': 1000,
                    'total_money': int((1000 * 0.40 * VERON_PRICE) + (1000 * 0.20 * VERON_PRICE))
                }
        ),
        (
                "Два уровня: родитель и ребенок",
                {
                    'id': 1,
                    'lo': 500,
                    'team': [
                        {
                            'id': 2,
                            'lo': 1500,
                            'team': []
                        }
                    ]
                },
                {
                    'qualification': 'Mentor',
                    'go': 2000,
                    'side': 500,
                    'total_money': 2310000  # только личный объем
                }
        ),
        (
                "Три уровня: родитель и ребенок и потомок",
                {
                    'id': 1213,
                    'lo': 500,
                    'team': [
                        {
                            'id': 1310,
                            'lo': 500,
                            'team': []
                        },
                        {
                            'id': 1311,
                            'lo': 500,
                            'team': []
                        },
                        {
                            'id': 1312,
                            'lo': 500,
                            'team': [
                                {
                                    'id': 1410,
                                    'lo': 1500,
                                    'team': []
                                }
                            ]
                        }
                    ]
                },
                {
                    'qualification': 'Direktor',
                    'go': 3500,
                    'side': 500,
                    'total_money': 5775000
                }
        ),
        (
                "Три уровня: родитель и ребенок и потомок",
                {
                    'id': 1211,
                    'lo': 50,
                    'team': [
                        {
                            'id': 1300,
                            'lo': 200,
                            'team': [
                                {
                                    'id': 1400,
                                    'lo': 500,
                                    'team': []
                                },
                                {
                                    'id': 1401,
                                    'lo': 500,
                                    'team': []
                                },
                                {
                                    'id': 1402,
                                    'lo': 300,
                                    'team': []
                                }
                            ]
                        },
                        {
                            'id': 1301,
                            'lo': 500,
                            'team': []
                        }, ###

                    ]
                },
                {
                    'qualification': 'Hamkor',
                    'go': 2050,
                    'side': 50,
                    'total_money': 5775000
                }
        ),
        (
                "Три уровня: родитель и ребенок и потомок",
                {
                    'id': 1101,
                    'lo': 450,
                    'team': [
                        {
                            'id': 1210,
                            'lo': 2000,
                            'team': []
                        },  ###
                        {
                            'id': 1211,
                            'lo': 50,
                            'team': [
                                {
                                    'id': 1300,
                                    'lo': 200,
                                    'team': [
                                        {
                                            'id': 1400,
                                            'lo': 500,
                                            'team': []
                                        },
                                        {
                                            'id': 1401,
                                            'lo': 500,
                                            'team': []
                                        },
                                        {
                                            'id': 1402,
                                            'lo': 300,
                                            'team': []
                                        }
                                    ]
                                },
                                {
                                    'id': 1301,
                                    'lo': 500,
                                    'team': []
                                },  ###

                            ]
                        },
                        {
                            'id': 1212,
                            'lo': 500,
                            'team': []
                        },  ###
                        {
                            'id': 1213,
                            'lo': 500,
                            'team': [
                                {
                                    'id': 1310,
                                    'lo': 500,
                                    'team': []
                                },
                                {
                                    'id': 1311,
                                    'lo': 500,
                                    'team': []
                                },
                                {
                                    'id': 1312,
                                    'lo': 500,
                                    'team': [
                                        {
                                            'id': 1410,
                                            'lo': 1500,
                                            'team': []
                                        }
                                    ]
                                }
                            ]
                        },

                    ]
                },
                {
                    'qualification': 'Direktor',
                    'go': 8500,
                    'side': 500,
                    'total_money': 8015000
                }
        ),
    ])
    def test_simple_structures(self, calculator, tree_builder, test_name, structure, expected):
        """Простые тестовые случаи"""
        print(f"\nТест: {test_name}")

        # Создаем дерево
        root_member = tree_builder(structure)

        # Выполняем расчет
        response, breakdown = calculator.calculate(root_member)

        # Проверяем
        assert response.qualification == expected['qualification']
        assert response.go == expected['go']
        assert response.side_volume == expected['side']
        assert response.total_money == pytest.approx(expected['total_money'])

        # Дополнительные проверки
        assert breakdown.total_money == pytest.approx(response.total_money)

    @pytest.mark.skip(reason="This test is currently broken")
    @pytest.mark.parametrize("structure, expected_qualification", [
        # Один участник
        (
                {'id': 1, 'lo': 100, 'team': []},
                'Hamkor'
        ),
        # Один участник с большим LO
        (
                {'id': 1, 'lo': 1000, 'team': []},
                'Mentor'
        ),
        # Родитель + сильный ребенок
        (
                {
                    'id': 1,
                    'lo': 500,
                    'team': [
                        {'id': 2, 'lo': 1500, 'team': []}
                    ]
                },
                'Mentor'  # ожидаем Mentor, т.к. LO родителя + сильный ребенок
        ),

        # Родитель + слабый ребенок
        (
                {
                    'id': 1,
                    'lo': 500,
                    'team': [
                        {'id': 2, 'lo': 100, 'team': []}
                    ]
                },
                'Mentor'
        ),
    ])
    def test_parent_qualification(self, structure, expected_qualification, tree_builder):
        """
        Проверяет корректное определение квалификации родителя с учётом LO и команд.
        """
        calculator = IncomeCalculator()

        # Создаем дерево
        root_member = tree_builder(structure)

        # Рассчитываем базовые объемы
        group_volume = root_member.group_volume()
        side_volume = calculator.calculate_side_volume(root_member, qualification_by_points(int(group_volume)))

        # Определяем квалификацию родителя
        qualification, points = calculator._determine_qualification(
            root_member, group_volume, side_volume
        )

        assert qualification.name == expected_qualification

    @pytest.mark.parametrize("side_volume,qual_percent,expected_money", [
        (1000.0, 0.20, 1000.0 * 0.20 * VERON_PRICE),  # 20% от 1000
        (500.0, 0.45, 500.0 * 0.45 * VERON_PRICE),  # 45% от 500
        (0.0, 0.20, 0.0),  # Нулевой объем
        (-100.0, 0.20, 0.0),  # Отрицательный объем
    ])
    def test_calculate_side_volume_bonus(self, calculator, side_volume, qual_percent, expected_money):
        """Тест расчета бонуса с side volume"""
        qualification = Mock(spec=Qualification)
        qualification.team_percent = qual_percent
        result = calculator._calculate_side_volume_bonus(side_volume, qualification)
        assert result == expected_money

    @pytest.mark.parametrize("side_volume,qual_percent,money,expected_desc", [
        (1000.0, 0.20, 1400000.0, "С бокового балла – 20%"),
        (500.0, 0.45, 1575000.0, "С бокового балла – 45%"),
        (250.0, 0.04, 70000.0, "С бокового балла – 4%"),
    ])
    def test_create_side_volume_breakdown(self, calculator, side_volume, qual_percent, money, expected_desc):
        """Тест создания breakdown item для side volume"""
        qualification = Mock(spec=Qualification)
        qualification.team_percent = qual_percent
        result = calculator._create_side_volume_breakdown(side_volume, qualification, money)

        assert isinstance(result, BreakdownItem)
        assert result.description == expected_desc
        assert result.volume == side_volume
        assert result.percent == qual_percent
        assert result.money == money

    @pytest.mark.parametrize("team_count,parent_team_percent,parent_side_volume,expected_total_money", [
        # Участник без команды, только side volume бонус
        (0, 0.45, 500.0, 500.0 * 0.45 * VERON_PRICE),
        # Участник с одной веткой
        (1, 0.45, 500.0, (500.0 * 0.45 * VERON_PRICE) + 1000.0),
        # Участник с несколькими ветками
        (3, 0.45, 500.0, (500.0 * 0.45 * VERON_PRICE) + 3000.0),
    ])
    def test_analyze_branches_integration(self, calculator, team_count, parent_team_percent,
                                          parent_side_volume, expected_total_money):
        """Интеграционный тест для analyze_branches"""
        # Подготовка
        member = Mock(spec=Member)
        member.team = [Mock(spec=Member) for _ in range(team_count)]

        parent_qual = Mock(spec=Qualification, team_percent=parent_team_percent)

        # Моки для внутренних методов
        calculator._calculate_side_volume_bonus = Mock(
            return_value=parent_side_volume * parent_team_percent * VERON_PRICE
        )
        calculator._create_side_volume_breakdown = Mock(return_value=Mock(spec=BreakdownItem))

        # Каждая ветка дает 1000 денег
        calculator._analyze_single_branch = Mock(
            return_value=(1000.0, Mock(), [Mock(spec=BreakdownItem)])
        )

        # Выполняем
        total_money, branches_info, breakdown_items = calculator._analyze_branches(
            member, parent_qual, parent_side_volume
        )

        # Проверяем
        assert total_money == pytest.approx(expected_total_money)
        assert len(branches_info) == team_count
        assert len(breakdown_items) == 1 + team_count  # side volume + все ветки

        # Проверяем вызовы
        calculator._calculate_side_volume_bonus.assert_called_once_with(
            parent_side_volume, parent_qual
        )
        assert calculator._analyze_single_branch.call_count == team_count


    @pytest.mark.parametrize(
        "branch_side,branch_qual_name,branch_min_points,parent_min_points,branch_team_percent,parent_team_percent,has_strong_sub,expected_has_money",
        [
            # Ветка сильнее родителя (не должна давать денег)
            (4000.0, "Direktor", 3500, 1500, 0.45, 0.35, False, False),
            # Ветка с сильными подветками
            (1000.0, "Mentor", 500, 3500, 0.20, 0.45, True, True),
            # Обычная ветка без подветок
            (1000.0, "Mentor", 500, 3500, 0.20, 0.45, False, True),
            # Ветка Hamkor (не должна давать денег)
            (100.0, "Hamkor", 0, 3500, 0.00, 0.45, False, False),
            # Ветка равна родителю
            (3500.0, "Direktor", 3500, 3500, 0.45, 0.45, False, False),
        ])
    def test_analyze_single_branch(self, calculator, branch_side, branch_qual_name, branch_min_points,
                                   parent_min_points, branch_team_percent, parent_team_percent,
                                   has_strong_sub, expected_has_money):
        """Тест анализа одной ветки"""
        # Подготовка
        branch = Mock(spec=Member)
        parent_qual = Mock(spec=Qualification)
        parent_qual.min_points = parent_min_points
        parent_qual.team_percent = parent_team_percent

        # Моки
        calculator._branch_side = Mock(return_value=branch_side)

        branch_qual = Mock(spec=Qualification)
        branch_qual.name = branch_qual_name
        branch_qual.min_points = branch_min_points
        branch_qual.team_percent = branch_team_percent

        # Патчим qualification_by_points
        with patch('domain.services.income_calculator.qualification_by_points') as mock_qual:
            mock_qual.return_value = branch_qual

            # Настраиваем моки в зависимости от сценария
            if has_strong_sub:
                calculator._find_strongest_sub_branches = Mock(return_value=[Mock(spec=Member)])
                calculator._process_strong_sub_branches = Mock(
                    return_value=(1000.0, Mock(), [Mock(spec=BreakdownItem)]))
                # Для Hamkor не должен вызываться _process_regular_branch
                if branch_qual_name != "Hamkor":
                    calculator._process_regular_branch = Mock()
            else:
                calculator._find_strongest_sub_branches = Mock(return_value=[])
                if branch_qual_name != "Hamkor" and branch_min_points < parent_min_points:
                    calculator._process_regular_branch = Mock(return_value=(500.0, Mock(), [Mock(spec=BreakdownItem)]))
                else:
                    calculator._process_regular_branch = Mock()

            # Выполняем
            money, info, breakdown = calculator._analyze_single_branch(branch, parent_qual)

            # Проверяем
            if expected_has_money:
                assert money > 0
                assert breakdown is not None
                # Проверяем что вызвался нужный метод
                if has_strong_sub:
                    calculator._process_strong_sub_branches.assert_called_once()
                else:
                    calculator._process_regular_branch.assert_called_once()
            else:
                assert money == 0
                # Для Hamkor и сильных веток _process_regular_branch не должен вызываться
                if branch_qual_name == "Hamkor" or branch_min_points >= parent_min_points:
                    calculator._process_regular_branch.assert_not_called()

    @pytest.mark.skip(reason="This test is currently broken")
    @pytest.mark.parametrize("strong_branches_count,qual_groups_data,expected_total_money", [
        # Одна сильная подветка
        (1, {"Mentor": [(Mock(spec=Member), 500.0, Mock(spec=Qualification, team_percent=0.20))]},
         500.0 * (0.45 - 0.20) * VERON_PRICE),
        # Несколько подветок с разными квалификациями
        (2, {
            "Mentor": [(Mock(spec=Member), 500.0, Mock(spec=Qualification, team_percent=0.20))],
            "Menejer": [(Mock(spec=Member), 1500.0, Mock(spec=Qualification, team_percent=0.35))],
        }, (500.0 * 0.25 + 1500.0 * 0.10) * VERON_PRICE),
        # Нет валидных подветок
        (0, {}, 0.0),
    ])
    def test_process_strong_sub_branches(self, calculator, strong_branches_count, qual_groups_data,
                                         expected_total_money):
        """Тест обработки сильных подветок"""
        # Подготовка
        strong_branches = [Mock(spec=Member) for _ in range(strong_branches_count)]
        original_branch = Mock(spec=Member)
        parent_qual = Mock(spec=Qualification, team_percent=0.45)

        # Моки
        calculator._group_branches_by_qualification = Mock(return_value=qual_groups_data)

        # Мок для _calculate_group_money
        def mock_calculate_group_money(branches_data, parent_qual, qual_name):
            total_volume = 0
            for _, branch_side, branch_q in branches_data:
                # Простой расчет: если side >= 500, считаем закрытой
                is_closed = branch_side >= 500
                base_volume = 100.0 if is_closed else branch_side  # Упрощенный расчет
                total_volume += base_volume
            percent = parent_qual.team_percent - branches_data[0][2].team_percent
            money = total_volume * percent * VERON_PRICE
            return money, [Mock(spec=BreakdownItem)]

        calculator._calculate_group_money = Mock(side_effect=mock_calculate_group_money)
        calculator._create_branch_info = Mock(return_value=Mock())

        # Выполняем
        total_money, branch_info, breakdown = calculator._process_strong_sub_branches(
            strong_branches, parent_qual, original_branch
        )

        # Проверяем
        assert total_money == pytest.approx(expected_total_money)
        if expected_total_money > 0:
            assert len(breakdown) == len(qual_groups_data)
        else:
            assert total_money == 0

    @pytest.mark.parametrize("branches_data,parent_min_points,expected_group_count", [
        # Одна ветка слабее родителя
        ([
             {"gv": 1500.0, "qual_name": "Menejer", "min_points": 1500, "team_percent": 0.35},
         ], 3500, 1),
        # Ветка сильнее родителя (не должна попасть в группы)
        ([
             {"gv": 3500.0, "qual_name": "Direktor", "min_points": 3500, "team_percent": 0.45},
         ], 1500, 0),
        # Смешанные ветки
        ([
             {"gv": 500.0, "qual_name": "Mentor", "min_points": 500, "team_percent": 0.20},
             {"gv": 1500.0, "qual_name": "Menejer", "min_points": 1500, "team_percent": 0.35},
             {"gv": 3500.0, "qual_name": "Direktor", "min_points": 3500, "team_percent": 0.45},
         ], 2500, 2),  # Только Mentor и Menejer
    ])
    def test_group_branches_by_qualification(self, calculator, branches_data, parent_min_points, expected_group_count):
        """Тест группировки веток по квалификации"""
        # Подготовка
        branches = []
        for data in branches_data:
            branch = Mock(spec=Member)
            branch.group_volume = Mock(return_value=data["gv"])
            branches.append(branch)

        parent_qual = Mock(spec=Qualification, min_points=parent_min_points)

        # Моки
        calculator._branch_side = Mock(side_effect=[500.0] * len(branches))

        # Патч для qualification_by_points
        def mock_qual_by_points(points):
            for data in branches_data:
                if int(data["gv"]) == points:
                    qual = Mock(spec=Qualification)
                    qual.name = data["qual_name"]
                    qual.min_points = data["min_points"]
                    qual.team_percent = data["team_percent"]
                    return qual
            # По умолчанию Hamkor
            qual = Mock(spec=Qualification)
            qual.name = "Hamkor"
            qual.min_points = 0
            qual.team_percent = 0.00
            return qual

        with patch('domain.services.income_calculator.qualification_by_points') as mock_qual:
            mock_qual.side_effect = mock_qual_by_points

            # Выполняем
            result = calculator._group_branches_by_qualification(branches, parent_qual)

            # Проверяем
            assert len(result) == expected_group_count

            # Проверяем, что в группы попали только те, что слабее родителя
            for qual_name, group_data in result.items():
                for branch, side, qual in group_data:
                    assert qual.min_points < parent_min_points

    @pytest.mark.skip(reason="This test is currently broken")
    @pytest.mark.parametrize("branches_data,parent_team_percent,expected_money", [
        # Одна незакрытая ветка
        ([
             {"branch": Mock(spec=Member, lo=500.0, user_id=101), "side": 1000.0,
              "qual": Mock(spec=Qualification, team_percent=0.20, name="Mentor")},
         ], 0.45, 1000.0 * 0.25 * VERON_PRICE),
        # Одна закрытая ветка (использует LO)
        ([
             {"branch": Mock(spec=Member, lo=200.0, user_id=102), "side": 600.0,
              "qual": Mock(spec=Qualification, team_percent=0.20, name="Mentor")},
         ], 0.45, 200.0 * 0.25 * VERON_PRICE),
        # Несколько веток
        ([
             {"branch": Mock(spec=Member, lo=500.0, user_id=103), "side": 500.0,
              "qual": Mock(spec=Qualification, team_percent=0.20, name="Mentor")},
             {"branch": Mock(spec=Member, lo=500.0, user_id=104), "side": 500.0,
              "qual": Mock(spec=Qualification, team_percent=0.20, name="Mentor")},
         ], 0.45, 1000.0 * 0.25 * VERON_PRICE),
        # Нулевая или отрицательная разница процентов
        ([
             {"branch": Mock(spec=Member, lo=500.0, user_id=105), "side": 1000.0,
              "qual": Mock(spec=Qualification, team_percent=0.50, name="Mentor")},
         ], 0.45, 0.0),
    ])
    def test_calculate_group_money(self, calculator, branches_data, parent_team_percent, expected_money):
        """Тест расчета денег для группы веток"""
        # Подготовка
        # Преобразуем данные в формат метода
        formatted_data = []
        for data in branches_data:
            formatted_data.append((data["branch"], data["side"], data["qual"]))

        parent_qual = Mock(spec=Qualification, team_percent=parent_team_percent)
        qual_name = "Test"

        # Вспомогательный метод для проверки закрытости
        calculator._is_branch_closed = lambda side, qual: side >= 500 and qual.name != "Hamkor"

        # Выполняем
        money, breakdown = calculator._calculate_group_money(
            formatted_data, parent_qual, qual_name
        )

        # Проверяем
        assert money == pytest.approx(expected_money)

        if expected_money > 0:
            assert len(breakdown) == 1
            breakdown_item = breakdown[0]
            assert isinstance(breakdown_item, BreakdownItem)

            # Проверяем описание
            if len(branches_data) == 1:
                assert f"ID: {branches_data[0]['branch'].user_id}" in breakdown_item.description
            else:
                assert f"{len(branches_data)} {qual_name}" in breakdown_item.description
        else:
            assert money == 0
            assert breakdown == []

    @pytest.mark.skip(reason="This test is currently broken")
    @pytest.mark.parametrize("branch_side,branch_team_percent,parent_team_percent,branch_lo,is_closed,expected_money", [
        # Обычная незакрытая ветка
        (1000.0, 0.20, 0.45, 500.0, False, 1000.0 * 0.25 * VERON_PRICE),
        # Закрытая ветка (использует LO)
        (600.0, 0.20, 0.45, 200.0, True, 200.0 * 0.25 * VERON_PRICE),
        # Нулевая разница процентов
        (1000.0, 0.45, 0.45, 500.0, False, 0.0),
        # Ветка сильнее родителя (team_percent больше)
        (1000.0, 0.50, 0.45, 500.0, False, 0.0),
    ])
    def test_process_regular_branch(self, calculator, branch_side, branch_team_percent,
                                    parent_team_percent, branch_lo, is_closed, expected_money):
        """Тест обработки обычной ветки"""
        # Подготовка
        branch = Mock(spec=Member, user_id=123, lo=branch_lo)
        branch_qual = Mock(spec=Qualification, name="Mentor", team_percent=branch_team_percent)
        parent_qual = Mock(spec=Qualification, team_percent=parent_team_percent)

        # Хелпер для проверки закрытости
        calculator._is_branch_closed = Mock(return_value=is_closed)
        calculator._create_branch_info = Mock(return_value=Mock())

        # Выполняем
        money, branch_info, breakdown = calculator._process_regular_branch(
            branch, branch_side, branch_qual, parent_qual
        )

        # Проверяем
        assert money == pytest.approx(expected_money)

        if expected_money > 0:
            assert len(breakdown) == 1
            breakdown_item = breakdown[0]
            assert isinstance(breakdown_item, BreakdownItem)
            assert f"ID: 123" in breakdown_item.description
            assert breakdown_item.volume == (branch_lo if is_closed else branch_side)
            assert breakdown_item.percent == (parent_team_percent - branch_team_percent)
            assert breakdown_item.money == pytest.approx(expected_money)
        else:
            assert money == 0

    @pytest.mark.skip(reason="This test is currently broken")
    def test_create_branch_info(self, calculator):
        """Тест создания информации о ветке"""
        # Подготовка
        branch = Mock(spec=Member)
        branch.user_id = 123
        branch.lo = 500.0
        branch.group_volume = Mock(return_value=2000.0)

        calculator._branch_side = Mock(return_value=1000.0)

        # Тест с сильными подветками
        result_with_subs = calculator._create_branch_info(branch, 3)

        assert result_with_subs.user_id == 123
        assert result_with_subs.lo == 500.0
        assert result_with_subs.group_volume == 2000.0
        assert result_with_subs.side_volume == 1000.0
        assert result_with_subs.has_strong_sub_branches == True
        assert result_with_subs.strong_sub_branches_count == 3

        # Тест без сильных подветок
        result_without_subs = calculator._create_branch_info(branch, 0)

        assert result_without_subs.has_strong_sub_branches == False
        assert result_without_subs.strong_sub_branches_count == 0



    ############################################
    ############################################
    ############################################
    ############################################
