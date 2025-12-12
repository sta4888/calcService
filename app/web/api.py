from fastapi import APIRouter

from app.web.schemas import MemberInput
from app.application.calculate_income import IncomeCalculatorUseCase

router = APIRouter()
use_case = IncomeCalculatorUseCase()

@router.post("/calculate", response_model=dict)
def calculate_income(payload: MemberInput):
    result = use_case.execute(payload.dict())
    return result
