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
    lo: float
    gv: float
    side_volume: float
    is_closed: bool  # Закрыла ли квалификацию по side volume
    is_stronger_than_parent: bool  # Сильнее ли родителя
    parent_earn_percent: float  # Сколько % получает родитель с этой ветки
    parent_earn_money: float  # Сколько денег получает родитель с этой ветки


class IncomeResponse(BaseModel):
    user_id: int
    qualification: str
    lo: float
    go: float
    side_volume: float
    points: float
    personal_bonus: float
    structure_bonus: float
    mentor_bonus: float
    extra_bonus: str
    personal_money: int
    group_money: int
    leader_money: int
    total_money: int
    veron: int
    total_income: float
    branches_info: List[BranchInfo]  # НОВОЕ ПОЛЕ


class AddLORequest(BaseModel):
    lo: float


class MemberStatus(BaseModel):
    user_id: int
    lo: float
    go: float
    level: float
    personal_bonus: float
    structure_bonus: float
    total_income: float
    team: List["MemberStatus"] = Field(default_factory=list)


MemberStatus.model_rebuild()
