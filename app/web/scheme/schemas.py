from pydantic import BaseModel, Field
from typing import Any, Optional

from typing import List, Dict, Any
from pydantic import BaseModel

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    error: bool = Field(..., description="Признак ошибки", example=False)
    data: Optional[T] = Field(
        None,
        description="Полезная нагрузка ответа"
    )
    error_msg: Optional[str] = Field(
        None,
        description="Сообщение об ошибке",
        example="User not found"
    )


class CalculateIncomeRequest(BaseModel):
    user_id: int = Field(..., description="ID участника", example=1001)


class BranchInfo(BaseModel):
    """Отладочная информация по ветке структуры"""

    branch_id: int = Field(..., description="ID участника в ветке")
    branch_qualification_by_gv: str = Field(
        ..., description="Квалификация ветки по групповому обороту (GV)"
    )
    branch_qualification_by_side: str = Field(
        ..., description="Квалификация ветки по side volume"
    )
    lo: int = Field(..., description="Личный оборот ветки")
    gv: int = Field(..., description="Групповой оборот ветки")
    side_volume: int = Field(..., description="Side volume ветки")
    is_closed: bool = Field(
        ..., description="Закрыта ли квалификация по side volume"
    )
    is_stronger_than_parent: bool = Field(
        ..., description="Является ли ветка сильнее родительского узла"
    )
    parent_earn_percent: int = Field(
        ..., description="Процент дохода родителя с этой ветки"
    )
    parent_earn_money: int = Field(
        ..., description="Сумма дохода родителя с этой ветки"
    )
    level: int = Field(..., description="Уровень ветки в структуре")


class IncomeResponse(BaseModel):
    user_id: int = Field(..., description="ID участника")
    qualification: str = Field(..., description="Текущая квалификация")
    lo: float = Field(..., description="Личный оборот (LO)")
    go: float = Field(..., description="Групповой оборот (GO)")
    group_side_volume: float = Field(0.0, description="Групповой оборот (GO)")
    side_volume: float = Field(..., description="Side volume")
    points: float = Field(..., description="Квалификационные баллы")

    personal_bonus: float = Field(..., description="Персональный бонус")
    structure_bonus: float = Field(..., description="Бонус структуры")
    mentor_bonus: float = Field(..., description="Менторский бонус")
    extra_bonus: str = Field(..., description="Дополнительные бонусы")

    personal_money: int = Field(..., description="Доход с личных продаж")
    group_money: int = Field(..., description="Доход с группового оборота")
    leader_money: int = Field(..., description="Лидерский бонус")
    side_vol_money: int = Field(..., description="Доход с side volume")

    total_money: int = Field(..., description="Общий доход в деньгах")
    veron: float = Field(..., description="Доход в Veron")
    total_income: float = Field(..., description="Итоговый доход")

    branches_info: List[BranchInfo] = Field(
        ..., description="Отладочная информация по веткам структуры"
    )


class AddLORequest(BaseModel):
    lo: float = Field(
        ...,
        gt=0,
        description="Личный оборот (LO)",
        example=1500.75
    )


class MemberStatus(BaseModel):
    user_id: int = Field(..., description="ID участника")
    lo: int = Field(..., description="Личный оборот")
    go: int = Field(..., description="Групповой оборот")
    level: int = Field(..., description="Уровень в структуре")

    personal_bonus: float = Field(..., description="Персональный бонус")
    structure_bonus: float = Field(..., description="Структурный бонус")
    total_income: float = Field(..., description="Суммарный доход")

    team: List["MemberStatus"] = Field(
        default_factory=list,
        description="Подчинённые участники"
    )


MemberStatus.model_rebuild()
