import pytest

from infrastructure.db.models import MemberDB, MemberStatsDB
from infrastructure.db.session import async_session
from domain.repositories.member_repository import MemberRepository


@pytest.mark.asyncio
async def test_build_member_tree_simple():
    repo = MemberRepository()

    async with async_session() as session:
        async with session.begin():
            root = MemberDB(user_id=1)
            root.stats = MemberStatsDB(lo=100)

            child1 = MemberDB(user_id=2, referrer=root)
            child1.stats = MemberStatsDB(lo=50)

            child2 = MemberDB(user_id=3, referrer=root)
            child2.stats = MemberStatsDB(lo=0)

            session.add_all([root, child1, child2])

    tree = await repo.build_member_tree(1)

    assert tree.user_id == 1
    assert tree.lo == 100
    assert len(tree.team) == 2

    user_ids = {m.user_id for m in tree.team}
    assert user_ids == {2, 3}