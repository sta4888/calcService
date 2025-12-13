from fastapi import APIRouter
from app.web.schemas import MemberInput
from app.application.calculate_income import IncomeCalculatorUseCase

router = APIRouter()
use_case = IncomeCalculatorUseCase()


@router.post("/calculate", response_model=dict)
async def calculate_income(payload: MemberInput):
    # payload.model_dump() может вернуть None, используем {} по умолчанию
    data = payload.model_dump() or {}

    # execute всегда возвращает dict (см. UseCase ниже)
    result = use_case.execute(data) or {}

    # дополнительная защита: если всё равно None, вернуть пустой dict
    if result is None:
        result = {}

    return result
