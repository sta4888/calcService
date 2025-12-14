from pydantic import BaseModel

class NewUserRequest(BaseModel):
    user_id: int
    referrer_id: int | None = None