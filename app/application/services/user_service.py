from application.mappers.member_mapper import member_to_tree_response
from domain.repositories.member_repository import MemberRepository
from domain.exceptions import DomainError
from domain.services.income_calculator import IncomeCalculator
from infrastructure.db.models import MemberDB, MemberStatsDB


class UserService:
    def __init__(self, repo: MemberRepository):
        self.repo = repo
        self.calculator = IncomeCalculator()

    async def create(self, user_id: int, referrer_user_id: int | None = None) -> MemberDB:
        existing = await self.repo.get_by_user_id(user_id)
        if existing:
            raise DomainError("User already exists")

        referrer_id: int | None = None
        if referrer_user_id is not None:
            referrer = await self.repo.get_by_user_id(referrer_user_id)
            if referrer:
                referrer_id = referrer.id  # теперь используем внутренний PK

        member = MemberDB(
            user_id=user_id,
            referrer_id=referrer_id,
            name=""
        )

        member.stats = MemberStatsDB(lo=0)

        await self.repo.save(member)
        return member

    async def add_lo(self, user_id: int, delta: float):
        if delta <= 0:
            raise DomainError("Delta must be positive")

        member = await self.repo.get_by_user_id(user_id)
        if not member or not member.stats:
            raise DomainError("User not found")

        member.stats.lo += delta
        await self.repo.save(member)

    async def sub_lo(self, user_id: int, delta: float):
        if delta <= 0:
            raise DomainError("Delta must be positive")

        member = await self.repo.get_by_user_id(user_id)
        if not member or not member.stats:
            raise DomainError("User not found")

        member.stats.lo = max(0, member.stats.lo - delta)
        await self.repo.save(member)

    async def get_status(self, user_id: int) -> dict:
        root_member = await self.repo.build_member_tree(user_id)
        # result = self.calculator.calculate(root_member)
        response, breakdown = self.calculator.calculate(root_member)

        # Получаем отформатированный отчет
        report = self.calculator.format_breakdown_report(breakdown)
        print(report)
        return response.dict()

    async def get_structure(self, user_id: int) -> dict:
        root_member = await self.repo.build_member_tree(user_id)
        return member_to_tree_response(root_member).dict()
