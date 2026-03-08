from fastapi import APIRouter, Depends
from application.services.user_service import UserService
from domain.repositories.member_repository import MemberRepository
from web.scheme.schemas import ApiResponse, AddLORequest, MemberStatus, IncomeResponse
from web.scheme.user import NewUserRequest, CreateUserResponse, AddLOResponse, SubLOResponse, MemberTreeResponse, \
    ResetLOResponse

user = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def get_user_service():
    repo = MemberRepository()
    return UserService(repo)


@user.post(
    "",
    summary="Создать нового пользователя",
    description="""
    Создаёт нового участника MLM-сети.

    - user_id должен быть уникальным
    - referrer_id — необязательный (корень сети)
    """,
    response_model=ApiResponse[CreateUserResponse],
    responses={
        200: {"description": "Пользователь успешно создан"},
        400: {"description": "Некорректные данные"},
    },
)
async def create_user(
        payload: NewUserRequest,
        service: UserService = Depends(get_user_service),
):
    member = await service.create(payload.user_id, payload.referrer_id)
    return ApiResponse(error=False, data={"user_id": member.user_id})


@user.post(
    "/{user_id}/lo/add",
    summary="Добавить личный оборот (LO)",
    description="Увеличивает личный оборот пользователя",
    response_model=ApiResponse[AddLOResponse],
)
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


@user.post(
    " /{user_id}/reset",
    summary="Сброс личный оборот (LO)",
    description="Сбрасывает личный оборот пользователя",
    response_model=ApiResponse[ResetLOResponse],
)
async def reset_lo(
        user_id: int,
        service: UserService = Depends(get_user_service),

):
    await service.reset_lo(user_id)
    return ApiResponse(
        error=False,
        data={"user_id": user_id},
    )


@user.post(
    "/{user_id}/lo/subtract",
    summary="Уменьшить личный оборот (LO)",
    description="Уменьшает личный оборот пользователя",
    response_model=ApiResponse[SubLOResponse],
)
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


@user.get(
    "/{user_id}/status",
    summary="Получить статус пользователя",
    description="Возвращает текущую квалификацию и обороты пользователя",
    response_model=ApiResponse[IncomeResponse],
)
async def user_status(
        user_id: int,
        service: UserService = Depends(get_user_service)
):
    result = await service.get_status(user_id)
    return ApiResponse(error=False, data=result)


@user.get(
    "/{user_id}/structure",
    summary="Получить структуру пользователя",
    description="Возвращает дерево структуры MLM",
    response_model=ApiResponse[MemberTreeResponse],
)
async def user_structure(
        user_id: int,
        service: UserService = Depends(get_user_service),
):
    result = await service.get_structure(user_id)
    return ApiResponse(error=False, data=result)
