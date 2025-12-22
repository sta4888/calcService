from domain.models.member import Member
from web.scheme.user import MemberTreeResponse


def member_to_tree_response(member: Member) -> MemberTreeResponse:
    return MemberTreeResponse(
        user_id=member.user_id,
        lo=member.lo,
        team=[
            member_to_tree_response(child)
            for child in member.team
        ]
    )