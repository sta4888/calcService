from domain.repositories.member_repository import MemberRepository
from domain.services.everon_calculator import EveronCalculator
from web.scheme.schemas import IncomeResponse


class IncomeService:
    def __init__(self, repo: MemberRepository):
        self.repo = repo
        self.calculator = EveronCalculator()

    async def calculate(self, user_id: int) -> IncomeResponse:
        root = await self.repo.build_member_tree(user_id)
        return self.calculator.calculate(root)
