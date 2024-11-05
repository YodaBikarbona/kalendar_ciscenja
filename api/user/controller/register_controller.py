from fastapi import (
    APIRouter,
    Body,
)
from starlette import status

from api.config import settings
from api.exception.bad_request import BadRequestException
from api.exception.internal_server_error import InternalServerErrorException
from api.user.serializer.request.register import NewUser
from api.user.service.user_service import register_user
from api.utils.response_utils import (
    ok_response,
    error_response,
)

router = APIRouter(
    prefix=f'{settings.route}/register',
    tags=['register'],
)


@router.post('')
async def register(data: NewUser = Body(...)):
    try:
        register_user(data)
        return ok_response(message='Successfully registered!', status_code=status.HTTP_201_CREATED)
    except (BadRequestException, InternalServerErrorException) as e:
        return error_response(message=e.message, status_code=e.status_code)
