import pytest
from unittest.mock import AsyncMock

from application.services.user_service import UserService
from domain.models.member import Member


@pytest.mark.asyncio
async def test_get_structure_returns_tree_dict():
    fake_repo = AsyncMock()

    fake_repo.build_member_tree.return_value = Member(
        user_id=1,
        referrer_id=None,
        lo=100,
        team=[
            Member(
                user_id=2,
                referrer_id=1,
                lo=50,
                team=[]
            )
        ]
    )

    service = UserService(repo=fake_repo)

    result = await service.get_structure(1)

    assert result["user_id"] == 1
    assert result["lo"] == 100
    assert len(result["team"]) == 1
    assert result["team"][0]["user_id"] == 2