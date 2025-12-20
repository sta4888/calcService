import pytest
from domain.models.member import Member


def test_group_volume_single_member():
    m = Member(user_id=1, lo=100)
    assert m.group_volume() == 100


def test_group_volume_with_team():
    root = Member(1, lo=100)
    a = Member(2, lo=200)
    b = Member(3, lo=300)

    root.team = [a, b]

    assert root.group_volume() == 600


def test_group_volume_deep_structure():
    root = Member(1, lo=100)
    a = Member(2, lo=200)
    b = Member(3, lo=50)
    c = Member(4, lo=150)

    a.team = [b]
    b.team = [c]
    root.team = [a]

    assert root.group_volume() == 500
