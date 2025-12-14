from fastapi import APIRouter
from app.web.schemas import MemberInput, IncomeResponse
from app.application.calculate_income import IncomeCalculatorUseCase

router = APIRouter()
use_case = IncomeCalculatorUseCase()


@router.post("/calculate", response_model=IncomeResponse)
async def calculate_income(payload: MemberInput):
    return use_case.execute(payload.model_dump())

