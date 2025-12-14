from fastapi import APIRouter

from web.scheme.schemas import ApiResponse, MemberInput, IncomeResponse
from application.calculate_income import IncomeCalculator
from domain.exceptions import DomainError
from web.utils import build_member_from_payload

claculate = APIRouter()
calculator = IncomeCalculator()


@claculate.post("/calculate", response_model=ApiResponse)
async def calculate_income(payload: MemberInput): # todo Исправить MemberInput так, чтоб отправлялся ID пользователя а получали на выходе уже скалькулированные данные, а данные для калькуляции должны браться из БД
    try:
        # пытаемся построить доменный объект
        root = build_member_from_payload(payload.model_dump())
    except Exception as e:
        return ApiResponse(error=True, data=None, error_msg=f"Invalid payload: {e}")


    try:
        # рассчитываем доход
        result = calculator.calculate(root)
        if not isinstance(result, IncomeResponse):
            # защита от None или неверного возврата
            raise DomainError("Calculation failed, result is not a dict")

        return ApiResponse(error=False, data=result)

    except DomainError as e:
        return ApiResponse(error=True, data=None, error_msg=str(e))
    except Exception as e:
        return ApiResponse(error=True, data=None, error_msg=f"Internal server error: {e}")


