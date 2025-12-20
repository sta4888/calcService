from domain.models.member import Member


def test_group_volume_single():
    member = Member(user_id=1, lo=100)
    assert member.group_volume() == 100


def test_group_volume_with_team():
    member = Member(
        user_id=1,
        lo=100,
        team=[
            Member(user_id=2, lo=200),
            Member(user_id=3, lo=300),
        ],
    )

    assert member.group_volume() == 600



def test_group_volume_deep_structure():
    member = Member(
        user_id=1,
        lo=100,
        team=[
            Member(
                user_id=2,
                lo=200,
                team=[
                    Member(user_id=3, lo=300)
                ],
            )
        ],
    )

    assert member.group_volume() == 600

