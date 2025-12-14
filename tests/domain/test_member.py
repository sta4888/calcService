from app.domain.models.member import Member


def test_group_volume_single():
    member = Member(name="A", lo=100)
    assert member.group_volume() == 100


def test_group_volume_with_team():
    member = Member(
        name="A",
        lo=100,
        team=[
            Member("B", 200),
            Member("C", 300),
        ],
    )

    assert member.group_volume() == 600


def test_group_volume_deep_structure():
    member = Member(
        name="A",
        lo=100,
        team=[
            Member(
                "B",
                200,
                team=[Member("C", 300)],
            )
        ],
    )

    assert member.group_volume() == 600
