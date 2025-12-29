from domain.models.member import Member

def m(
    user_id: int,
    lo: float,
    team=None
):
    return Member(
        user_id=user_id,
        lo=lo,
        team=team or []
    )