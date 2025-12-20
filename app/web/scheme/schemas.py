from typing import List
from pydantic import BaseModel, Field
from typing import Any, Optional


class ApiResponse(BaseModel):
    error: bool
    data: Optional[Any] = None
    error_msg: Optional[str] = ""


class CalculateIncomeRequest(BaseModel):
    user_id: int



class IncomeResponse(BaseModel):
    user_id: int
    qualification: str
    lo: float
    go: float
    points: float
    personal_bonus: float
    structure_bonus: float
    mentor_bonus: float
    extra_bonus: str
    veron: float
    total_income: float





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
