from sqlalchemy import select

from domain.exceptions import DomainError
from domain.models.member import Member
from infrastructure.db.session import async_session
from infrastructure.db.models import MemberDB


class MemberRepository:
    def __init__(self, session_factory=None):
        self._session_factory = session_factory or async_session

    async def get_by_user_id(self, user_id: int) -> MemberDB | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(MemberDB)
                .where(MemberDB.user_id == user_id)
            )
            return result.scalars().first()

    async def get_by_referrer_id(self, referrer_id: int) -> list[MemberDB]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(MemberDB)
                .where(MemberDB.referrer_id == referrer_id)
            )
            return result.scalars().all()

    async def save(self, member: MemberDB):
        async with self._session_factory() as session:
            async with session.begin():
                session.add(member)

    async def build_member_tree(self, user_id: int) -> "Member":
        root_db = await self.get_by_user_id(user_id)
        if not root_db:
            raise DomainError("User not found")

        return await self._build_recursive(root_db)

    async def _build_recursive(self, db_member: MemberDB) -> "Member":
        children_db = await self.get_by_referrer_id(db_member.id)

        children = [
            await self._build_recursive(child)
            for child in children_db
        ]

        return Member(
            user_id=db_member.user_id,
            referrer_id=db_member.referrer_id,
            lo=db_member.lo,
            team=children
        )
