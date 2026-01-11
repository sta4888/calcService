from pydantic import BaseModel, Field
from typing import List


class NewUserRequest(BaseModel):
    user_id: int = Field(..., description="ID нового участника", example=1001)
    referrer_id: int | None = Field(
        None,
        description="ID пригласившего участника",
        example=500
    )


class CreateUserResponse(BaseModel):
    user_id: int = Field(..., description="ID созданного пользователя")


class AddLOResponse(BaseModel):
    user_id: int
    lo_added: float


class SubLOResponse(BaseModel):
    user_id: int
    lo_subtracted: float


class MemberTreeResponse(BaseModel):
    user_id: int = Field(..., description="ID участника")
    lo: float = Field(..., description="Личный оборот")
    team: List["MemberTreeResponse"] = Field(
        default_factory=list,
        description="Подчинённые участники"
    )

    class Config:
        orm_mode = True


MemberTreeResponse.update_forward_refs()
