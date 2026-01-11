from fastapi import APIRouter, Depends

from domain.exceptions import DomainError
from web.scheme.schemas import ApiResponse, CalculateIncomeRequest, IncomeResponse
from application.services.income_service import IncomeService
from domain.repositories.member_repository import MemberRepository

calculate = APIRouter(
    prefix="/income",
    tags=["Income"],
)


def get_income_service():
    repo = MemberRepository()
    return IncomeService(repo)

@calculate.post(
    "/calculate",
    summary="Рассчитать доход пользователя",
    description="""
    Выполняет полный расчёт дохода:
    - личный оборот
    - групповой оборот
    - лидерский бонус
    - квалификация
    """,
    response_model=ApiResponse[IncomeResponse],
    responses={
        200: {"description": "Доход успешно рассчитан"},
        400: {"description": "Ошибка доменной логики"},
    },
)
async def calculate_income(
    payload: CalculateIncomeRequest,
    service: IncomeService = Depends(get_income_service)
):
    try:
        result = await service.calculate(payload.user_id)
        return ApiResponse(error=False, data=result)
    except DomainError as e:
        return ApiResponse(error=True, error_msg=str(e))

