from typing import List
from pydantic import BaseModel, Field
from typing import Any, Optional


class ApiResponse(BaseModel):
    error: bool
    data: Optional[Any] = None
    error_msg: Optional[str] = ""


class CalculateIncomeRequest(BaseModel):
    user_id: int


from typing import List, Dict, Any
from pydantic import BaseModel


class BranchInfo(BaseModel):
    """Информация о ветке для отладки"""
    branch_id: int
    branch_qualification_by_gv: str  # Квалификация по group volume
    branch_qualification_by_side: str  # Квалификация по side volume
    lo: int
    gv: int
    side_volume: int
    is_closed: bool  # Закрыла ли квалификацию по side volume
    is_stronger_than_parent: bool  # Сильнее ли родителя
    parent_earn_percent: int  # Сколько % получает родитель с этой ветки
    parent_earn_money: int  # Сколько денег получает родитель с этой ветки
    level: int


class IncomeResponse(BaseModel):
    user_id: int
    qualification: str
    lo: int
    go: int
    side_volume: int
    points: int
    personal_bonus: float
    structure_bonus: float
    mentor_bonus: float
    extra_bonus: str
    personal_money: int
    group_money: int
    leader_money: int
    total_money: int
    veron: int
    total_income: int
    branches_info: List[BranchInfo]  # НОВОЕ ПОЛЕ


class AddLORequest(BaseModel):
    lo: int


class MemberStatus(BaseModel):
    user_id: int
    lo: int
    go: int
    level: int
    personal_bonus: float
    structure_bonus: float
    total_income: float
    team: List["MemberStatus"] = Field(default_factory=list)


MemberStatus.model_rebuild()
