# tests/conftest.py
import pytest
from unittest.mock import Mock
from domain.models.member import Member
from domain.services.income_calculator import IncomeCalculator
from domain.value_objects.qualification import Qualification


@pytest.fixture
def calculator():
    """Фикстура калькулятора"""
    return IncomeCalculator()


@pytest.fixture
def mock_member_factory():
    """Фабрика для создания моков участников"""

    def create_member(user_id, lo=0, team=None):
        """Создает мок участника"""
        member = Mock(spec=Member)
        member.user_id = user_id
        member.lo = float(lo)
        member.team = team or []

        # Вычисляем group_volume
        def calc_group_volume():
            total = member.lo
            for child in member.team:
                total += child.group_volume.return_value
            return total

        member.group_volume.return_value = calc_group_volume()

        return member

    return create_member


@pytest.fixture
def tree_builder(mock_member_factory):
    """Строитель деревьев участников"""

    def build_tree(structure):
        """
        Строит дерево из структуры:
        {
            'id': 1,
            'lo': 100,
            'team': [
                {'id': 2, 'lo': 50, 'team': []},
                ...
            ]
        }
        """

        def _build_node(node_data):
            # Рекурсивно строим детей
            children = []
            for child_data in node_data.get('team', []):
                child_node = _build_node(child_data)
                children.append(child_node)

            # Создаем участника
            member = mock_member_factory(
                user_id=node_data['id'],
                lo=node_data['lo'],
                team=children
            )

            return member

        return _build_node(structure)

    return build_tree


@pytest.fixture
def hamkor_member(mock_member_factory):
    """Участник с квалификацией Hamkor"""
    return mock_member_factory(user_id=1, lo=50)


@pytest.fixture
def mentor_member(mock_member_factory):
    """Участник с квалификацией Mentor"""
    return mock_member_factory(user_id=2, lo=300)


@pytest.fixture
def simple_two_level_tree(tree_builder):
    """Простое двухуровневое дерево"""
    return tree_builder({
        'id': 1,
        'lo': 500,
        'team': [
            {
                'id': 2,
                'lo': 100,
                'team': []
            }
        ]
    })


@pytest.fixture
def tree_with_strong_branch(tree_builder):
    """Дерево с сильной веткой"""
    return tree_builder({
        'id': 1,
        'lo': 600,  # Mentor
        'team': [
            {
                'id': 2,
                'lo': 600,  # Тоже Mentor (сильная)
                'team': [
                    {
                        'id': 3,
                        'lo': 100,
                        'team': []
                    }
                ]
            }
        ]
    })


@pytest.fixture
def complex_tree(tree_builder):
    """Сложное дерево с несколькими уровнями"""
    return tree_builder({
        'id': 1,
        'lo': 1000,  # Menejer
        'team': [
            {
                'id': 2,
                'lo': 600,  # Mentor
                'team': [
                    {
                        'id': 3,
                        'lo': 200,
                        'team': []
                    }
                ]
            },
            {
                'id': 4,
                'lo': 400,  # Hamkor
                'team': []
            }
        ]
    })



@pytest.fixture
def calculator():
    return IncomeCalculator()


@pytest.fixture
def sample_member():
    """Создает тестового участника"""
    member = Mock(spec=Member)
    member.user_id = 1
    member.lo = 100.0
    member.team = []
    return member


@pytest.fixture
def sample_qualification():
    """Создает тестовую квалификацию"""
    return Qualification(
        name="Mentor",
        min_points=500,
        personal_percent=0.40,
        team_percent=0.20,
        mentor_percent=0.02,
        extra_bonus="Par dazmol"
    )


@pytest.fixture
def direktor_qualification():
    """Квалификация Direktor для тестов"""
    return Qualification(
        name="Direktor",
        min_points=3500,
        personal_percent=0.40,
        team_percent=0.45,
        mentor_percent=0.04,
        extra_bonus="Televizor smart-32"
    )


@pytest.fixture
def menejer_qualification():
    """Квалификация Menejer для тестов"""
    return Qualification(
        name="Menejer",
        min_points=1500,
        personal_percent=0.40,
        team_percent=0.35,
        mentor_percent=0.03,
        extra_bonus="Changyutgich"
    )


@pytest.fixture
def complex_branch_structure():
    """Создает сложную структуру веток для тестов"""
    # Создаем mock-объекты для дерева
    branch1 = Mock(spec=Member)
    branch1.user_id = 101
    branch1.lo = 500.0
    branch1.team = []

    branch2 = Mock(spec=Member)
    branch2.user_id = 102
    branch2.lo = 1500.0
    branch2.team = []

    sub_branch = Mock(spec=Member)
    sub_branch.user_id = 201
    sub_branch.lo = 1000.0
    sub_branch.team = []

    branch3 = Mock(spec=Member)
    branch3.user_id = 103
    branch3.lo = 200.0
    branch3.team = [sub_branch]

    return [branch1, branch2, branch3]