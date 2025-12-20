from fastapi import APIRouter, Depends
from application.services.user_service import UserService
from domain.repositories.member_repository import MemberRepository
from web.scheme.schemas import ApiResponse, AddLORequest
from web.scheme.user import NewUserRequest

user = APIRouter()


def get_user_service():
    repo = MemberRepository()
    return UserService(repo)


@user.post("/users")
async def create_user(
        payload: NewUserRequest,
        service: UserService = Depends(get_user_service),
):
    member = await service.create(payload.user_id, payload.referrer_id)
    return ApiResponse(error=False, data={"user_id": member.user_id})


@user.post("/users/{user_id}/lo/add")
async def add_lo(
        user_id: int,
        payload: AddLORequest,
        service: UserService = Depends(get_user_service),
):
    await service.add_lo(user_id, payload.lo)
    return ApiResponse(
        error=False,
        data={"user_id": user_id, "lo_added": payload.lo},
    )


@user.post("/users/{user_id}/lo/subtract")
async def sub_lo(
        user_id: int,
        payload: AddLORequest,
        service: UserService = Depends(get_user_service),
):
    await service.sub_lo(user_id, payload.lo)
    return ApiResponse(
        error=False,
        data={"user_id": user_id, "lo_subtracted": payload.lo},
    )


@user.get("/users/{user_id}/status")
async def user_status(user_id: int, service: UserService = Depends(get_user_service)):
    result = await service.get_status(user_id)
    return ApiResponse(error=False, data=result)
