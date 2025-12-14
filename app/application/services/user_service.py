from domain.repositories.member_repository import MemberRepository
from domain.exceptions import DomainError
from infrastructure.db.models import MemberDB

class UserService:
    def __init__(self, repo: MemberRepository):
        self.repo = repo

    async def create(self, user_id: int, referrer_id: int | None = None) -> MemberDB:
        existing = await self.repo.get_by_user_id(user_id)
        if existing:
            raise DomainError("User already exists")

        # Проверка реферала
        if referrer_id is not None:
            referrer = await self.repo.get_by_user_id(referrer_id)
            if not referrer:
                referrer_id = None  # можно оставить None, если реферал не найден

        member = MemberDB(
            user_id=user_id,
            referrer_id=referrer_id,
            lo=0,
            name=""
        )

        await self.repo.add(member)
        return member

    async def add_lo(self, user_id: int, lo: float) -> None:
        member = await self.repo.get_by_user_id(user_id)
        if not member:
            raise DomainError("User not found")

        member.lo += lo
        await self.repo.update(member)

    async def get_status(self, user_id: int) -> dict:
        member = await self.repo.get_by_user_id(user_id)
        if not member:
            raise DomainError("User not found")

        # Пример расчёта группового объёма
        group_volume = sum(m.lo for m in member.team)
        return {
            "user_id": member.user_id,
            "lo": member.lo,
            "group_volume": group_volume
        }
