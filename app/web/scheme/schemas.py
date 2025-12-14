from typing import List
from pydantic import BaseModel
from typing import Any, Optional


class ApiResponse(BaseModel):
    error: bool
    data: Optional[Any] = None
    error_msg: Optional[str] = ""


class MemberInput(BaseModel):
    name: str
    lo: float
    team: List["MemberInput"] = []

# MemberInput.update_forward_refs()


class IncomeResponse(BaseModel):
    name: str
    lo: float
    go: float
    level: float
    personal_bonus: float
    structure_bonus: float
    total_income: float


# class MemberInput(BaseModel):
#     user_id: int
#     referrer_id: Optional[int] = None


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
    team: List["MemberStatus"] = []


MemberStatus.model_rebuild()
