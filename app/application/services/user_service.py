from domain.repositories.member_repository import MemberRepository
from domain.exceptions import DomainError
from domain.services.income_calculator import IncomeCalculator
from infrastructure.db.models import MemberDB


class UserService:
    def __init__(self, repo: MemberRepository):
        self.repo = repo
        self.calculator = IncomeCalculator()

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

        await self.repo.save(member)
        return member

    async def add_lo(self, user_id: int, delta: float):
        member = await self.repo.get_by_user_id(user_id)
        if not member:
            raise DomainError("User not found")

        member.lo += delta
        await self.repo.save(member)

    async def sub_lo(self, user_id: int, delta: float):
        if delta <= 0:
            raise DomainError("Delta must be positive")

        member = await self.repo.get_by_user_id(user_id)
        if not member:
            raise DomainError("User not found")

        member.lo = max(0, member.lo - delta)
        await self.repo.save(member)

    async def get_status(self, user_id: int) -> dict:
        # 1. Строим дерево участников
        root_member = await self.repo.build_member_tree(user_id)

        # 2. Рассчитываем доход через калькулятор
        result = self.calculator.calculate(root_member)

        # 3. Возвращаем
        return result.dict()  # если используешь Pydantic-схему
