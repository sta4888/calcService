from typing import List, Optional
from sqlalchemy import select
from infrastructure.db.session import async_session
from infrastructure.db.models import MemberDB

class MemberRepository:
    def __init__(self, session_factory=None):
        self._session_factory = session_factory or async_session

    async def add(self, member: MemberDB):
        async with self._session_factory() as session:
            async with session.begin():
                session.add(member)

    async def get_by_user_id(self, user_id: int) -> Optional[MemberDB]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(MemberDB).where(MemberDB.user_id == user_id)
            )
            return result.scalars().first()

    async def list_team(self, user_id: int) -> List[MemberDB]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(MemberDB).where(MemberDB.referrer_id == user_id)
            )
            return result.scalars().all()

    async def update(self, member: MemberDB):
        async with self._session_factory() as session:
            async with session.begin():
                session.add(member)
