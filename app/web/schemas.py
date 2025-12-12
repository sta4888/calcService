from pydantic import BaseModel
from typing import List

class MemberInput(BaseModel):
    name: str
    lo: float
    team: List["MemberInput"] = []

MemberInput.update_forward_refs()


class IncomeResponse(BaseModel):
    name: str
    lo: float
    go: float
    level: float
    personal_bonus: float
    structure_bonus: float
    total_income: float
