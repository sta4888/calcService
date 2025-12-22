from pydantic import BaseModel
from typing import List


class NewUserRequest(BaseModel):
    user_id: int
    referrer_id: int | None = None


class MemberTreeResponse(BaseModel):
    user_id: int
    lo: float
    team: List["MemberTreeResponse"] = []

    class Config:
        orm_mode = True


MemberTreeResponse.update_forward_refs()
