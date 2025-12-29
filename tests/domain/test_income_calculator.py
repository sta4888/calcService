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
        # (
        #         "Три уровня: родитель и ребенок и потомок",
        #         {
        #             'id': 1211,
        #             'lo': 50,
        #             'team': [
        #                 {
        #                     'id': 1300,
        #                     'lo': 200,
        #                     'team': [
        #                         {
        #                             'id': 1400,
        #                             'lo': 500,
        #                             'team': []
        #                         },
        #                         {
        #                             'id': 1401,
        #                             'lo': 500,
        #                             'team': []
        #                         },
        #                         {
        #                             'id': 1402,
        #                             'lo': 300,
        #                             'team': []
        #                         }
        #                     ]
        #                 },
        #                 {
        #                     'id': 1301,
        #                     'lo': 500,
        #                     'team': []
        #                 }, ###
        #
        #             ]
        #         },
        #         {
        #             'qualification': 'Hamkor',
        #             'go': 2050,
        #             'side': 50,
        #             'total_money': 5775000
        #         }
        # ),
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


    # def test_comprehensive_calculation(self, calculator, complex_tree):
    #     """Комплексный тест расчета"""
    #     # Arrange
    #     root_member = complex_tree
    #
    #     # Act
    #     response, breakdown = calculator.calculate(root_member)
    #
    #     # Assert
    #     print(f"\nКомплексный тест:")
    #     print(f"  Квалификация: {response.qualification}")
    #     print(f"  LO: {response.lo}")
    #     print(f"  GO: {response.go}")
    #     print(f"  Side volume: {response.side_volume}")
    #     print(f"  Total money: {response.total_money}")
    #
    #     # Проверяем что квалификация определена
    #     assert response.qualification in ['Hamkor', 'Mentor', 'Menejer', 'Direktor',
    #                                       'Bronza', 'Kumush', 'Oltin', 'Zumrad', 'Brilliant', 'Olmos']
    #
    #     # Проверяем что все значения неотрицательные
    #     assert response.lo >= 0
    #     assert response.go >= response.lo  # GO всегда >= LO
    #     assert response.side_volume >= 0
    #     assert response.total_money >= 0
    #
    #     # Проверяем детализацию
    #     total_from_breakdown = 0
    #     for item in breakdown.personal_items:
    #         total_from_breakdown += item.money
    #     for item in breakdown.group_items:
    #         total_from_breakdown += item.money
    #     for item in breakdown.leader_items:
    #         total_from_breakdown += item.money
    #
    #     assert total_from_breakdown == pytest.approx(response.total_money, rel=0.01)
    #
    # @pytest.mark.parametrize("structure, expected_qualification", [
    #     # Простые случаи
    #     ({'id': 1, 'lo': 100, 'team': []}, 'Hamkor'),
    #     ({'id': 1, 'lo': 500, 'team': []}, 'Mentor'),
    #     ({'id': 1, 'lo': 1500, 'team': []}, 'Menejer'),
    #
    #     # С командой
    #     ({
    #          'id': 1,
    #          'lo': 400,
    #          'team': [
    #              {'id': 2, 'lo': 200, 'team': []}
    #          ]
    #      }, 'Mentor'),  # 600 GV -> Mentor
    #
    #     ({
    #          'id': 1,
    #          'lo': 1000,
    #          'team': [
    #              {'id': 2, 'lo': 800, 'team': []}
    #          ]
    #      }, 'Menejer'),  # 1800 GV -> Menejer
    # ])
    # def test_qualification_determination(self, calculator, tree_builder,
    #                                      structure, expected_qualification):
    #     """Тест определения квалификации"""
    #     # Arrange
    #     root_member = tree_builder(structure)
    #
    #     # Act
    #     response, _ = calculator.calculate(root_member)
    #
    #     # Assert
    #     assert response.qualification == expected_qualification
    #
    # @pytest.mark.parametrize("parent_lo, child_lo, expected_go_money", [
    #     # Родитель Hamkor (40%), ребенок Hamkor (40%) -> разница 0%
    #     (100, 100, 0),
    #
    #     # Родитель Mentor (35%), ребенок Hamkor (40%) -> отрицательная разница, но должно быть 0
    #     (500, 100, 0),
    #
    #     # Родитель Menejer (40%), ребенок Mentor (35%) -> разница 5%
    #     (1000, 600, 600 * 0.05 * VERON_PRICE),
    #
    #     # Родитель Direktor (45%), ребенок Menejer (40%) -> разница 5%
    #     (3500, 1500, 1500 * 0.05 * VERON_PRICE),
    # ])
    # def test_group_money_calculation(self, calculator, tree_builder,
    #                                  parent_lo, child_lo, expected_go_money):
    #     """Тест расчета группового дохода"""
    #     # Arrange
    #     structure = {
    #         'id': 1,
    #         'lo': parent_lo,
    #         'team': [
    #             {'id': 2, 'lo': child_lo, 'team': []}
    #         ]
    #     }
    #     root_member = tree_builder(structure)
    #
    #     # Act
    #     response, breakdown = calculator.calculate(root_member)
    #
    #     # Assert
    #     # GO деньги не могут быть отрицательными
    #     assert response.group_money >= 0
    #
    #     # Если ожидаем положительные деньги, проверяем приблизительно
    #     if expected_go_money > 0:
    #         assert response.group_money == pytest.approx(expected_go_money, rel=0.1)
    #
    #     # Проверяем что в breakdown есть group items
    #     if response.group_money > 0:
    #         assert len(breakdown.group_items) > 0
    #
    # def test_leader_money_with_strong_branch(self, calculator, tree_with_strong_branch):
    #     """Тест лидерского дохода с сильной веткой"""
    #     # Arrange
    #     root_member = tree_with_strong_branch
    #
    #     # Act
    #     response, breakdown = calculator.calculate(root_member)
    #
    #     # Assert
    #     print(f"\nТест с сильной веткой:")
    #     print(f"  Leader money: {response.leader_money}")
    #     print(f"  Group money: {response.group_money}")
    #
    #     # При сильной ветке лидерские деньги должны быть > 0
    #     assert response.leader_money > 0
    #
    #     # При сильной ветке групповые деньги должны быть 0
    #     assert response.group_money == 0
    #
    #     # В breakdown должны быть leader items
    #     assert len(breakdown.leader_items) > 0
    #
    # @pytest.mark.parametrize("lo_volume, expected_percent", [
    #     (100, 0.40),  # Hamkor
    #     (500, 0.45),  # Mentor
    #     (1500, 0.50),  # Menejer
    #     (3500, 0.55),  # Direktor
    #     (10000, 0.60),  # Bronza
    # ])
    # def test_personal_bonus_percentages(self, calculator, mock_member_factory,
    #                                     lo_volume, expected_percent):
    #     """Тест процентов личного бонуса по квалификациям"""
    #     # Arrange
    #     member = mock_member_factory(user_id=1, lo=lo_volume)
    #
    #     # Act
    #     response, _ = calculator.calculate(member)
    #
    #     # Assert
    #     assert response.personal_bonus == pytest.approx(expected_percent, rel=0.01)
    #
    # def test_breakdown_formatting(self, calculator, simple_two_level_tree):
    #     """Тест форматирования детализации"""
    #     # Arrange
    #     root_member = simple_two_level_tree
    #
    #     # Act
    #     response, breakdown = calculator.calculate(root_member)
    #
    #     # Форматируем отчет
    #     report = calculator.format_breakdown_report(breakdown)
    #
    #     # Assert
    #     assert report is not None
    #     assert isinstance(report, str)
    #     assert len(report) > 0
    #
    #     # Проверяем наличие ключевых разделов
    #     assert "Личный:" in report
    #     assert "Командный:" in report
    #     assert "ИТОГО:" in report
    #
    #     # Проверяем что в отчете есть сумма
    #     assert f"{response.total_money:,.0f}" in report
    #
    #     print(f"\nОтчет:\n{report}")








# @pytest.mark.parametrize("test_name, structure, expected", [
#     (
#             "Базовый тест: один участник",
#             {
#                 'id': 1,
#                 'lo': 100,
#                 'team': []
#             },
#             {
#                 'qualification': 'Hamkor',
#                 'go': 100,
#                 'side': 100,
#                 'total_money': 100 * 0.40 * VERON_PRICE
#             }
#     ),
#     # (
#     #         "Два уровня: родитель и ребенок",
#     #         {
#     #             'id': 1,
#     #             'lo': 500,
#     #             'team': [
#     #                 {
#     #                     'id': 2,
#     #                     'lo': 100,
#     #                     'team': []
#     #                 }
#     #             ]
#     #         },
#     #         {
#     #             'qualification': 'Mentor',
#     #             'go': 600,
#     #             'side': 600,
#     #             'total_money': 500 * 0.45 * VERON_PRICE  # только личный объем
#     #         }
#     # ),
# ])
# def test_simple_structures(self, calculator, test_name, structure, expected):
#     """Простые тестовые случаи"""
#     print(f"\nТест: {test_name}")
#
#     # Создаем мок
#     root_member = self._create_member_tree(structure)
#
#     # Выполняем расчет
#     response, breakdown = calculator.calculate(root_member)
#
#     # Проверяем
#     assert response.qualification == expected['qualification']
#     assert response.go == expected['go']
#     assert response.side_volume == expected['side']
#     assert response.total_money == pytest.approx(expected['total_money'], rel=0.01)
#
# class TestIncomeCalculator:
#
#     @pytest.fixture
#     def calculator(self):
#         return IncomeCalculator()
#
#     @pytest.fixture
#     def mock_member(self):
#         member = Mock(spec=Member)
#         member.user_id = 1
#         member.lo = 100.0
#         member.group_volume.return_value = 1000.0
#         member.team = []
#         return member
#
#     @pytest.fixture
#     def hamkor_member(self):
#         """Создает участника с квалификацией Hamkor"""
#         member = Mock(spec=Member)
#         member.user_id = 2
#         member.lo = 50.0
#         member.team = []
#         member.group_volume.return_value = 50.0
#         return member
#
#     @pytest.fixture
#     def mentor_member(self):
#         """Создает участника с квалификацией Mentor"""
#         member = Mock(spec=Member)
#         member.user_id = 3
#         member.lo = 300.0
#         member.team = []
#         member.group_volume.return_value = 300.0
#         return member
#
#     # ==================== Тесты для _branch_side ====================
#
#     @pytest.mark.parametrize("lo, children_data, expected_side", [
#         (100, [], 100),
#         (500, [(1500, True)], 500),
#         (100, [(500, True), (500, True)], 100),
#         (450, [(2000, True), (50, False), (500, True), (500, True)], 500),
#     ])
#     def test_branch_side(self, calculator, lo, children_data, expected_side):
#         branch = Mock(spec=Member)
#         branch.lo = lo
#         branch.team = []
#
#         children = []
#         for i, (child_lo, is_closed) in enumerate(children_data):
#             child = Mock(spec=Member)
#             child.user_id = i + 1
#             child.lo = child_lo
#             child.team = []
#             children.append(child)
#             branch.team.append(child)
#
#         with patch.object(calculator, '_is_qualification_closed') as mock_is_closed:
#
#             def is_closed_side_effect(member):
#                 for i, child in enumerate(children):
#                     if member == child:
#                         return children_data[i][1]
#                 return False
#
#             mock_is_closed.side_effect = is_closed_side_effect
#
#             # Act
#             result = calculator._branch_side(branch)
#
#             # Assert
#             assert result == expected_side
#
#     # ==================== Тесты для _get_branch_qualification_by_side ====================
#
#     @pytest.mark.parametrize("side_volume, expected_qual_name", [
#         (0, "Hamkor"),
#         (100, "Hamkor"),
#         (499, "Hamkor"),
#         (500, "Mentor"),
#         (1000, "Mentor"),
#         (1499, "Mentor"),
#         (1500, "Menejer"),
#         (3500, "Direktor"),
#         (10000, "Bronza"),
#         (25000, "Kumush"),
#         (50000, "Oltin"),
#         (70000, "Zumrad"),
#         (85000, "Brilliant"),
#         (100000, "Olmos"),
#     ])
#     def test_get_branch_qualification_by_side(self, calculator, side_volume, expected_qual_name):
#         """Тест определения квалификации по side volume"""
#         # Arrange
#         branch = Mock(spec=Member)
#         branch.lo = side_volume / 2
#         branch.team = []
#
#         # Мокаем _branch_side для возврата заданного side_volume
#         calculator._branch_side = Mock(return_value=side_volume)
#
#         # Act
#         result = calculator._get_branch_qualification_by_side(branch)
#
#         # Assert
#         assert result.name == expected_qual_name
#
#     # ==================== Тесты для _has_equal_or_stronger_child ====================
#
#     @pytest.mark.parametrize("parent_points, child_points_list, expected_result", [
#         (500, [100, 200, 300], False),  # Все дети слабее
#         (500, [500, 200, 300], True),  # Один ребенок равен
#         (500, [600, 200, 300], True),  # Один ребенок сильнее
#         (500, [400, 450, 550], True),  # Последний ребенок сильнее
#         (500, [], False),  # Нет детей
#     ])
#     def test_has_equal_or_stronger_child(self, calculator, parent_points, child_points_list, expected_result):
#         """Тест проверки наличия детей с квалификацией >= родителя"""
#         # Arrange
#         parent = Mock(spec=Member)
#         parent.team = []
#
#         # Создаем детей с заданными квалификациями
#         children = []
#         for i, points in enumerate(child_points_list):
#             child = Mock(spec=Member)
#             child.user_id = i + 1
#             child.lo = points / 2
#             child.team = []
#             children.append(child)
#             parent.team.append(child)
#
#         # Создаем side_effect для мока
#         def get_qual_side_effect(member):
#             # Находим индекс ребенка
#             for i, child in enumerate(children):
#                 if member == child:
#                     return qualification_by_points(child_points_list[i])
#             return qualification_by_points(0)
#
#         calculator._get_branch_qualification_by_side = Mock(side_effect=get_qual_side_effect)
#
#         # Act
#         result = calculator._has_equal_or_stronger_child(parent, parent_points)
#
#         # Assert
#         assert result == expected_result
#
#     # # ==================== Тесты для _find_max_qualification_in_branch ====================
#
#     @pytest.mark.parametrize("branch_points, child_points_list, expected_qual_name", [
#         ([100], [], "Hamkor"),  # Только ветка Hamkor
#         ([500], [], "Mentor"),  # Только ветка Mentor
#         ([100], [500, 300], "Mentor"),  # Ветка Hamkor, дети Mentor и Hamkor
#         ([1500], [500, 1000], "Menejer"),  # Ветка Menejer, дети Mentor и Bronza
#         ([500], [1500, 3500], "Direktor"),  # Ветка Mentor, дети Menejer и Direktor
#         ([10000], [25000, 50000], "Oltin"),  # Ветка Bronza, дети Kumush и Oltin
#     ])
#     def test_find_max_qualification_in_branch(self, calculator, branch_points, child_points_list, expected_qual_name):
#         """Тест поиска максимальной квалификации в ветке"""
#         # Arrange
#         branch = Mock(spec=Member)
#         branch.user_id = 0
#         branch.team = []
#
#         # Создаем детей
#         children = []
#         for i, points in enumerate(child_points_list):
#             child = Mock(spec=Member)
#             child.user_id = i + 1
#             child.team = []
#             children.append(child)
#
#         branch.team = children
#
#         # Мокаем _get_branch_qualification_by_side для всех узлов
#         def get_qual_side_effect(node):
#             if node == branch:
#                 return qualification_by_points(branch_points[0])
#             else:
#                 # Находим индекс ребенка
#                 idx = next((i for i, c in enumerate(children) if c == node), -1)
#                 if idx >= 0:
#                     return qualification_by_points(child_points_list[idx])
#                 return qualification_by_points(0)
#
#         calculator._get_branch_qualification_by_side = Mock(side_effect=get_qual_side_effect)
#
#         # Act
#         result = calculator._find_max_qualification_in_branch(branch)
#
#         # Assert
#         assert result.name == expected_qual_name
#
#
#
#
#     # ==================== Тесты для _branch_side_contribution ====================
#
#     @pytest.mark.parametrize("branch_status, parent_min_points, branch_min_points, expected_contribution", [
#         # Закрытая ветка - учитываем только LO
#         ("closed", 500, 300, "branch.lo"),  # branch.lo = 100
#         ("closed", 500, 600, "branch.lo"),  # branch.lo = 100
#
#         # Сильная ветка (>= родителя) - не учитываем
#         ("open", 500, 500, 0),  # Равна родителю
#         ("open", 500, 600, 0),  # Сильнее родителя
#
#         # Открытая и слабая ветка - учитываем весь side volume
#         ("open", 500, 300, "full_side"),  # full_side = 200
#         ("open", 1000, 500, "full_side"),  # full_side = 300
#     ])
#     def test_branch_side_contribution(self, calculator, branch_status, parent_min_points,
#                                       branch_min_points, expected_contribution):
#         """Тест определения вклада ветки в side volume родителя"""
#         # Arrange
#         branch = Mock(spec=Member)
#         branch.lo = 100.0
#
#         parent_qual = Mock(spec=Qualification)
#         parent_qual.min_points = parent_min_points
#
#         branch_qual = Mock(spec=Qualification)
#         branch_qual.min_points = branch_min_points
#
#         # Мокаем методы
#         calculator._is_qualification_closed = Mock(
#             return_value=(branch_status == "closed")
#         )
#         calculator._get_branch_qualification_by_side = Mock(return_value=branch_qual)
#         calculator._branch_side = Mock(return_value=200.0)  # Предполагаемый side volume
#
#         # Act
#         result = calculator._branch_side_contribution(branch, parent_qual)
#
#         # Assert
#         if expected_contribution == "branch.lo":
#             assert result == 100.0  # branch.lo
#         elif expected_contribution == "full_side":
#             assert result == 200.0  # full side volume
#         else:
#             assert result == expected_contribution
#
#         # Проверяем вызовы
#         calculator._is_qualification_closed.assert_called_once_with(branch)
#         if branch_status != "closed" and branch_min_points < parent_min_points:
#             calculator._branch_side.assert_called_once_with(branch)
#
#
#     # ==================== Тесты для _get_branch_volume_for_go_calculation ====================
#
#     @pytest.mark.parametrize("is_closed, is_innermost, branch_lo, branch_side, expected_volume", [
#         # Закрытая и самая глубокая - только LO
#         (True, True, 100, 500, 100),
#
#         # Закрытая, но не самая глубокая - весь side volume
#         (True, False, 100, 500, 500),
#
#         # Открытая и самая глубокая - весь side volume
#         (False, True, 100, 500, 500),
#
#         # Открытая и не самая глубокая - весь side volume
#         (False, False, 100, 500, 500),
#
#         # Пограничные значения
#         (True, True, 0, 1000, 0),
#         (True, True, 1000, 1000, 1000),
#     ])
#     def test_get_branch_volume_for_go_calculation(self, calculator, is_closed, is_innermost,
#                                                   branch_lo, branch_side, expected_volume):
#         """Тест определения объема ветки для расчета ГО"""
#         # Arrange
#         branch = Mock(spec=Member)
#         branch.lo = branch_lo
#
#         # Мокаем методы
#         calculator._is_qualification_closed = Mock(return_value=is_closed)
#         calculator._branch_side = Mock(return_value=branch_side)
#
#         # Act
#         result = calculator._get_branch_volume_for_go_calculation(branch, is_innermost)
#
#         # Assert
#         assert result == expected_volume
#
#         # Проверяем вызовы
#         if is_closed and is_innermost:
#             calculator._is_qualification_closed.assert_called_once_with(branch)
#             calculator._branch_side.assert_not_called()
#         else:
#             calculator._is_qualification_closed.assert_called_once_with(branch)
#             calculator._branch_side.assert_called_once_with(branch)
#
#
#     # ==================== Тесты для _calculate_leader_money_with_breakdown ====================
#
#     @pytest.mark.parametrize("strong_go, mentor_percent, expected_money, expected_breakdown", [
#         # Нет сильных веток
#         (0, 0.02, 0, False),
#
#         # Есть сильные ветки
#         (1000, 0.02, 1000 * 0.02 * VERON_PRICE, True),
#         (5000, 0.05, 5000 * 0.05 * VERON_PRICE, True),
#         (10000, 0.10, 10000 * 0.10 * VERON_PRICE, True),
#
#         # Большие объемы
#         (50000, 0.07, 50000 * 0.07 * VERON_PRICE, True),
#         (100000, 0.10, 100000 * 0.10 * VERON_PRICE, True),
#     ])
#     def test_calculate_leader_money_with_breakdown(self, calculator, strong_go,
#                                                    mentor_percent, expected_money, expected_breakdown):
#         """Тест расчета денег за лидерство с детализацией"""
#         # Arrange
#         member = Mock(spec=Member)
#         qualification = Mock(spec=Qualification)
#         qualification.mentor_percent = mentor_percent
#
#         calculator._strong_branches_go = Mock(return_value=strong_go)
#
#         # Act
#         leader_money, leader_items = calculator._calculate_leader_money_with_breakdown(
#             member, qualification
#         )
#
#         # Assert
#         assert leader_money == pytest.approx(expected_money, rel=1e-10)
#
#         if expected_breakdown:
#             assert len(leader_items) == 1
#             item = leader_items[0]
#             assert item.volume == strong_go
#             assert item.percent == mentor_percent
#             assert item.money == pytest.approx(expected_money, rel=1e-10)
#             assert f"{mentor_percent * 100:.0f}%" in item.description
#         else:
#             assert len(leader_items) == 0
#
#         calculator._strong_branches_go.assert_called_once_with(member, qualification)
#
#     # ==================== Интеграционные тесты ====================
#
#     def test_calculate_full_scenario(self, calculator, mock_member):
#         """Интеграционный тест полного расчета"""
#         # Arrange
#         mock_member.group_volume.return_value = 1500  # Menejer
#         mock_member.lo = 200
#
#         # Создаем простую структуру
#         child1 = Mock(spec=Member)
#         child1.user_id = 101
#         child1.lo = 100
#         child1.group_volume.return_value = 600
#         child1.team = []
#
#         child2 = Mock(spec=Member)
#         child2.user_id = 102
#         child2.lo = 150
#         child2.group_volume.return_value = 800
#         child2.team = []
#
#         mock_member.team = [child1, child2]
#
#         # Мокаем вспомогательные методы
#         calculator._branch_side = Mock(
#             side_effect=lambda m: {
#                 mock_member: 450,  # 200 + 100 + 150
#                 child1: 100,
#                 child2: 150
#             }[m]
#         )
#
#         # Act
#         response, breakdown = calculator.calculate(mock_member)
#
#         # Assert
#         assert response.user_id == 1
#         assert response.lo == 200
#         assert response.go == 1500
#         assert response.side_volume == 450
#         assert breakdown.total_money > 0
#
#     def test_format_breakdown_report(self, calculator):
#         """Тест форматирования отчета"""
#         # Arrange
#         breakdown = IncomeBreakdown(
#             personal_items=[
#                 BreakdownItem(
#                     description="Личный объем – 40%",
#                     volume=100.0,
#                     percent=0.40,
#                     money=100 * 0.40 * VERON_PRICE
#                 )
#             ],
#             group_items=[
#                 BreakdownItem(
#                     description="С бокового балла – 35%",
#                     volume=500.0,
#                     percent=0.35,
#                     money=500 * 0.35 * VERON_PRICE
#                 )
#             ],
#             leader_items=[
#                 BreakdownItem(
#                     description="С сильных веток – 2%",
#                     volume=1000.0,
#                     percent=0.02,
#                     money=1000 * 0.02 * VERON_PRICE
#                 )
#             ],
#             total_money=10000.0
#         )
#
#         # Act
#         report = calculator.format_breakdown_report(breakdown)
#
#         # Assert
#         assert "Личный:" in report
#         assert "Командный:" in report
#         assert "Лидерский:" in report
#         assert "ИТОГО:" in report
#         assert f"{VERON_PRICE}" in report
#         assert "40%" in report
#         assert "35%" in report
#         assert "2%" in report
#
#     # ==================== Тесты для _check_children_for_qualification ====================
#
#     @pytest.mark.parametrize("target_points, children_points, expected_result", [
#         (500, [], False),  # Нет детей
#         (500, [100, 200, 300], False),  # Нет детей с такой квалификацией
#         (500, [100, 500, 300], True),  # Есть ребенок с такой квалификацией
#         (500, [500, 500, 500], True),  # Несколько детей с такой квалификацией
#         (500, [600, 700, 800], False),  # Дети с другой квалификацией
#     ])
#     def test_check_children_for_qualification(self, calculator, target_points, children_points, expected_result):
#         """Тест поиска детей с указанной квалификацией"""
#         # Arrange
#         node = Mock(spec=Member)
#         node.team = []
#
#         children = []
#         for i, points in enumerate(children_points):
#             child = Mock(spec=Member)
#             child.user_id = i + 1
#             children.append(child)
#             node.team.append(child)
#
#         # Создаем side_effect для мока
#         def get_qual_side_effect(member):
#             for i, child in enumerate(children):
#                 if member == child:
#                     qual_mock = Mock(spec=Qualification)
#                     qual_mock.min_points = children_points[i]
#                     return qual_mock
#             return Mock(min_points=0)
#
#         calculator._get_branch_qualification_by_side = Mock(side_effect=get_qual_side_effect)
#
#         # Act
#         result = calculator._check_children_for_qualification(node, target_points)
#
#         # Assert
#         assert result == expected_result
#
#     # ==================== Тесты для _find_all_branches_with_qualification ====================
#
#     @pytest.mark.parametrize("target_qual_name, node_qual_names, expected_count", [
#         ("Mentor", ["Hamkor", "Mentor", "Hamkor", "Mentor"], 2),  # 2 ветки Mentor
#         ("Direktor", ["Mentor", "Menejer", "Direktor"], 1),  # 1 ветка Direktor
#         ("Hamkor", ["Mentor", "Menejer", "Direktor"], 0),  # Нет веток Hamkor
#         ("Oltin", ["Oltin", "Oltin", "Oltin"], 3),  # 3 ветки Oltin
#         ("Bronza", [], 0),  # Пустая ветка
#     ])
#     def test_find_all_branches_with_qualification(self, calculator, target_qual_name, node_qual_names,
#                                                   expected_count):
#         """Тест поиска всех веток с указанной квалификацией"""
#         # Arrange
#         branch = Mock(spec=Member)
#
#         # Создаем дерево с заданными квалификациями
#         nodes = []
#         for i, qual_name in enumerate(node_qual_names):
#             node = Mock(spec=Member)
#             node.user_id = i + 1
#             node.team = []
#             nodes.append(node)
#
#         branch.team = nodes
#
#         # Мокаем квалификации
#         def get_qual_side_effect(node):
#             if node == branch:
#                 return qualification_by_points(0)
#             idx = next((i for i, n in enumerate(nodes) if n == node), -1)
#             if idx >= 0:
#                 qual_name = node_qual_names[idx]
#                 # Находим квалификацию по имени
#                 for points in [0, 500, 1500, 3500, 10000, 25000, 50000, 70000, 85000, 100000]:
#                     qual = qualification_by_points(points)
#                     if qual.name == qual_name:
#                         return qual
#             return qualification_by_points(0)
#
#         calculator._get_branch_qualification_by_side = Mock(side_effect=get_qual_side_effect)
#
#         # Находим target квалификацию
#         target_qual = None
#         for points in [0, 500, 1500, 3500, 10000, 25000, 50000, 70000, 85000, 100000]:
#             qual = qualification_by_points(points)
#             if qual.name == target_qual_name:
#                 target_qual = qual
#                 break
#
#         # Act
#         result = calculator._find_all_branches_with_qualification(branch, target_qual)
#
#         # Assert
#         assert len(result) == expected_count
#         if expected_count > 0:
#             assert all(calculator._get_branch_qualification_by_side(node).name == target_qual_name
#                        for node in result)
#
#     # ==================== Тесты для _is_qualification_closed ====================
#
#     # @pytest.mark.parametrize("side_volume, qual_name, has_strong_children, expected_result", [
#     #     (499, "Mentor", False, False),
#     #     (499, "Mentor", True, False),
#     #
#     #     (500, "Hamkor", False, True),
#     #     (1000, "Hamkor", True, True),
#     #
#     #     (500, "Mentor", False, False),
#     #     (1500, "Menejer", False, True),
#     #     (3500, "Direktor", False, True),
#     #
#     #     (500, "Mentor", True, False),
#     #     (1500, "Menejer", True, False),
#     # ])
#     # def test_is_qualification_closed(
#     #         self,
#     #         calculator,
#     #         side_volume,
#     #         qual_name,
#     #         has_strong_children,
#     #         expected_result,
#     # ):
#     #     # Arrange
#     #     branch = Mock(spec=Member)
#     #     branch.user_id = 1
#     #
#     #     calculator._raw_branch_side = Mock(return_value=side_volume)
#     #
#     #     qual_mock = Mock(spec=Qualification)
#     #     qual_mock.name = qual_name
#     #     qual_mock.min_points = 0 if qual_name == "Hamkor" else 500
#     #
#     #     calculator._get_branch_qualification_by_side = Mock(return_value=qual_mock)
#     #     calculator._has_equal_or_stronger_child = Mock(return_value=has_strong_children)
#     #
#     #     # Act
#     #     result = calculator._is_qualification_closed(branch)
#     #
#     #     # Assert
#     #     assert result == expected_result
#     #
#     #     calculator._raw_branch_side.assert_called_once_with(branch)
#     #
#     #     if side_volume >= SIDE_VOLUME_THRESHOLD:
#     #         calculator._get_branch_qualification_by_side.assert_called_once_with(branch)
#     #     else:
#     #         calculator._get_branch_qualification_by_side.assert_not_called()
#     #
#     #     if side_volume >= SIDE_VOLUME_THRESHOLD and qual_name != "Hamkor":
#     #         calculator._has_equal_or_stronger_child.assert_called_once_with(
#     #             branch, qual_mock.min_points
#     #         )
#     #     else:
#     #         calculator._has_equal_or_stronger_child.assert_not_called()
#
#
#
#
#
#     # # ==================== Тесты для calculate_side_volume ====================
#     #
#     # @pytest.mark.parametrize("member_lo, branches_data, expected_side_volume", [
#     #     # Без веток
#     #     (100, [], 100),
#     #
#     #     # С одной веткой
#     #     (100, [("closed", 500, 300, 50)], 100),  # 100 + 50 (только LO)
#     #     # (100, [("open", 500, 600, 200)], 100),  # 100 + 0 (сильная ветка)
#     #     # (100, [("open", 500, 300, 200)], 300),  # 100 + 200 (полный side)
#     #
#     #     # # С несколькими ветками
#     #     # (100, [
#     #     #     ("closed", 500, 300, 50),
#     #     #     ("open", 500, 600, 200),
#     #     #     ("open", 500, 300, 150)
#     #     # ], 300),  # 100 + 50 + 0 + 150 = 300
#     #     #
#     #     # # Все типы веток
#     #     # (200, [
#     #     #     ("closed", 1000, 500, 100),  # +100 (LO)
#     #     #     ("open", 1000, 1200, 300),  # +0 (сильная)
#     #     #     ("open", 1000, 800, 250),  # +250 (full side)
#     #     #     ("closed", 1000, 900, 120),  # +120 (LO)
#     #     # ], 670),  # 200 + 100 + 0 + 250 + 120 = 670
#     # ])
#     # def test_calculate_side_volume(self, calculator, member_lo, branches_data, expected_side_volume):
#     #     member = Mock(spec=Member)
#     #     member.lo = member_lo
#     #     member.team = []
#     #
#     #     parent_qual = Mock(spec=Qualification)
#     #     parent_qual.min_points = 1000
#     #
#     #     branch_to_contribution = {}
#     #
#     #     for i, (_, _, _, contribution) in enumerate(branches_data):
#     #         branch = Mock(spec=Member)
#     #         branch.user_id = i + 1
#     #         branch.lo = 0
#     #         branch.team = []
#     #
#     #         member.team.append(branch)
#     #         branch_to_contribution[branch] = contribution
#     #
#     #     def side_effect(branch_param, qual_param):
#     #         return branch_to_contribution.get(branch_param, 0)
#     #
#     #     calculator._branch_side_contribution = Mock(side_effect=side_effect)
#     #
#     #     # Act
#     #     result = calculator.calculate_side_volume(member, parent_qual)
#     #
#     #     # Assert
#     #     assert result == expected_side_volume
#
#     # # ==================== Тесты для _strong_branches_go ====================
#     #
#     # @pytest.mark.parametrize("member_qual_points, branches_data, expected_strong_go", [
#     #     # Нет сильных веток
#     #     (500, [(300, 400), (200, 350)], 0),
#     #
#     #     # Одна сильная ветка
#     #     (500, [(600, 800), (200, 350)], 800),  # 800 от первой ветки
#     #
#     #     # Несколько сильных веток
#     #     (500, [(600, 800), (700, 1200), (200, 350)], 2000),  # 800 + 1200
#     #
#     #     # Ветки равны родителю
#     #     (500, [(500, 600), (500, 700), (400, 300)], 1300),  # 600 + 700
#     #
#     #     # Все ветки слабее
#     #     (1000, [(500, 800), (600, 900), (700, 1000)], 0),
#     #
#     #     # Все ветки сильнее или равны
#     #     (300, [(500, 800), (400, 600), (300, 500)], 1900),  # 800 + 600 + 500
#     # ])
#     # def test_strong_branches_go(self, calculator, member_qual_points, branches_data, expected_strong_go):
#     #     """Тест расчета ГО сильных веток"""
#     #     # Arrange
#     #     member = Mock(spec=Member)
#     #     member.team = []
#     #
#     #     qualification = Mock(spec=Qualification)
#     #     qualification.min_points = member_qual_points
#     #
#     #     for i, (branch_qual_points, group_volume) in enumerate(branches_data):
#     #         branch = Mock(spec=Member)
#     #         branch.user_id = i + 1
#     #         branch.group_volume.return_value = group_volume
#     #
#     #         branch_qual = Mock(spec=Qualification)
#     #         branch_qual.min_points = branch_qual_points
#     #
#     #         # Мокаем квалификацию ветки
#     #         calculator._get_branch_qualification_by_side = Mock(
#     #             side_effect=lambda b: branch_qual if b == branch else Mock(min_points=0)
#     #         )
#     #
#     #         member.team.append(branch)
#     #
#     #     # Act
#     #     result = calculator._strong_branches_go(member, qualification)
#     #
#     #     # Assert
#     #     assert result == expected_strong_go
#     #
#     #     # Проверяем вызовы group_volume только для сильных веток
#     #     strong_count = sum(1 for qual_points, _ in branches_data
#     #                        if qual_points >= member_qual_points)
#     #     total_calls = sum(branch.group_volume.call_count for branch in member.team)
#     #     assert total_calls == strong_count
#     #
#     # # ==================== Тесты для _determine_qualification ====================
#     #
#     # @pytest.mark.parametrize("group_volume, side_volume, has_strong_branches, expected_points", [
#     #     # side >= 500 и нет сильных веток -> берем group_volume
#     #     (1500, 600, False, 1500),
#     #     (3500, 500, False, 3500),
#     #     (10000, 1000, False, 10000),
#     #
#     #     # side < 500 -> берем side_volume (даже если нет сильных веток)
#     #     (1500, 400, False, 400),
#     #     (3500, 499, False, 499),
#     #     (10000, 300, False, 300),
#     #
#     #     # есть сильные ветки -> берем side_volume (даже если side >= 500)
#     #     (1500, 600, True, 600),
#     #     (3500, 1000, True, 1000),
#     #     (10000, 500, True, 500),
#     #
#     #     # side < 500 и есть сильные ветки -> берем side_volume
#     #     (1500, 400, True, 400),
#     #     (3500, 300, True, 300),
#     # ])
#     # def test_determine_qualification(self, calculator, group_volume, side_volume,
#     #                                  has_strong_branches, expected_points):
#     #     """Тест определения финальной квалификации"""
#     #     # Arrange
#     #     member = Mock(spec=Member)
#     #     member.team = [Mock()] if has_strong_branches else []
#     #
#     #     # Мокаем _branch_side для каждой ветки
#     #     def branch_side_side_effect(branch):
#     #         # Возвращаем достаточно большой side volume для создания сильной ветки
#     #         return 2000 if has_strong_branches else 100
#     #
#     #     calculator._branch_side = Mock(side_effect=branch_side_side_effect)
#     #
#     #     # Act
#     #     result_qual, result_points = calculator._determine_qualification(
#     #         member, group_volume, side_volume
#     #     )
#     #
#     #     # Assert
#     #     assert result_points == expected_points
#     #     expected_qual = qualification_by_points(int(expected_points))
#     #     assert result_qual.name == expected_qual.name
#     #     assert result_qual.min_points == expected_qual.min_points
#
#
#     def test_is_qualification_closed(self, calculator):
#         """Тест проверки закрытия квалификации"""
#         # Arrange
#         branch = Mock(spec=Member)
#         branch.user_id = 1
#
#         # Ситуация 1: side volume < порога -> не закрыт
#         calculator._raw_branch_side = Mock(return_value=499)
#         result = calculator._is_qualification_closed(branch)
#         assert result == False
#
#         # Ситуация 2: side volume >= порога, но квалификация Hamkor -> не закрыт
#         calculator._raw_branch_side = Mock(return_value=500)
#         qual_mock = Mock(spec=Qualification)
#         qual_mock.name = "Hamkor"
#         qual_mock.min_points = 0
#         calculator._get_branch_qualification_by_side = Mock(return_value=qual_mock)
#         result = calculator._is_qualification_closed(branch)
#         assert result == False
#
#         # Ситуация 3: side volume >= порога, квалификация не Hamkor, есть сильные дети -> не закрыт
#         calculator._raw_branch_side = Mock(return_value=1500)
#         qual_mock.name = "Menejer"
#         qual_mock.min_points = 1500
#         calculator._get_branch_qualification_by_side = Mock(return_value=qual_mock)
#         calculator._has_equal_or_stronger_child = Mock(return_value=True)
#         result = calculator._is_qualification_closed(branch)
#         assert result == False
#
#         # Ситуация 4: side volume >= порога, квалификация не Hamkor, нет сильных детей -> закрыт
#         calculator._has_equal_or_stronger_child = Mock(return_value=False)
#         result = calculator._is_qualification_closed(branch)
#         assert result == True
#
#     def test_calculate_side_volume(self, calculator):
#         """Тест расчета side volume"""
#         # Arrange
#         member = Mock(spec=Member)
#         member.lo = 100
#         member.team = []
#
#         parent_qual = Mock(spec=Qualification)
#         parent_qual.min_points = 1000
#
#         # Ситуация 1: нет веток
#         calculator._branch_side_contribution = Mock(return_value=0)
#         result = calculator.calculate_side_volume(member, parent_qual)
#         assert result == 100  # только личный объем
#
#         # Ситуация 2: есть ветка, закрытая
#         child1 = Mock(spec=Member)
#         member.team = [child1]
#
#         def contribution_side_effect(branch, qual):
#             if branch == child1:
#                 return 50  # только LO закрытой ветки
#             return 0
#
#         calculator._branch_side_contribution = Mock(side_effect=contribution_side_effect)
#         result = calculator.calculate_side_volume(member, parent_qual)
#         assert result == 150  # 100 + 50
#
#         # Ситуация 3: есть сильная ветка
#         def contribution_side_effect2(branch, qual):
#             if branch == child1:
#                 return 0  # сильная ветка не учитывается
#             return 0
#
#         calculator._branch_side_contribution = Mock(side_effect=contribution_side_effect2)
#         result = calculator.calculate_side_volume(member, parent_qual)
#         assert result == 100  # только личный объем
#
#         def test_strong_branches_go(self, calculator):
#             """Тест расчета ГО сильных веток"""
#             # Arrange
#             member = Mock(spec=Member)
#             member.team = []
#
#             qualification = Mock(spec=Qualification)
#             qualification.min_points = 500  # Mentor
#
#             # Создаем детей
#             child1 = Mock(spec=Member)
#             child1.user_id = 101
#             child1.group_volume.return_value = 800
#
#             child2 = Mock(spec=Member)
#             child2.user_id = 102
#             child2.group_volume.return_value = 600
#
#             child3 = Mock(spec=Member)
#             child3.user_id = 103
#             child3.group_volume.return_value = 400
#
#             member.team = [child1, child2, child3]
#
#             # Мокаем квалификации детей
#             def get_qual_side_effect(branch):
#                 if branch == child1:
#                     qual_mock = Mock(spec=Qualification)
#                     qual_mock.min_points = 600  # сильнее родителя
#                     return qual_mock
#                 elif branch == child2:
#                     qual_mock = Mock(spec=Qualification)
#                     qual_mock.min_points = 500  # равна родителю
#                     return qual_mock
#                 else:
#                     qual_mock = Mock(spec=Qualification)
#                     qual_mock.min_points = 400  # слабее родителя
#                     return qual_mock
#
#             calculator._get_branch_qualification_by_side = Mock(side_effect=get_qual_side_effect)
#
#             # Act
#             result = calculator._strong_branches_go(member, qualification)
#
#             # Assert
#             # Только child1 и child2 должны учитываться
#             assert result == 1400  # 800 + 600
#             child1.group_volume.assert_called_once()
#             child2.group_volume.assert_called_once()
#             child3.group_volume.assert_not_called()
#
#     def test_determine_qualification(self, calculator):
#         """Тест определения финальной квалификации"""
#         # Arrange
#         member = Mock(spec=Member)
#
#         # Ситуация 1: side >= 500 и нет сильных веток -> берем group_volume
#         group_volume = 1500
#         side_volume = 600
#
#         # Мокаем проверку сильных веток
#         calculator._branch_side = Mock(return_value=100)  # все дети слабые
#         member.team = [Mock(), Mock()]
#
#         result_qual, result_points = calculator._determine_qualification(
#             member, group_volume, side_volume
#         )
#         assert result_points == 1500  # берем group_volume
#         assert result_qual.name == "Menejer"
#
#         # Ситуация 2: side < 500 -> берем side_volume
#         side_volume = 400
#         result_qual, result_points = calculator._determine_qualification(
#             member, group_volume, side_volume
#         )
#         assert result_points == 400  # берем side_volume
#         assert result_qual.name == "Hamkor"
#
#         # Ситуация 3: есть сильные ветки -> берем side_volume
#         side_volume = 600
#
#         def branch_side_side_effect(branch):
#             # Возвращаем большой volume для создания сильной ветки
#             return 2000
#
#         calculator._branch_side = Mock(side_effect=branch_side_side_effect)
#
#         result_qual, result_points = calculator._determine_qualification(
#             member, group_volume, side_volume
#         )
#         assert result_points == 600  # берем side_volume