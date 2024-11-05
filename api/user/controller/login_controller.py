from fastapi import (
    APIRouter,
    Body,
)
from starlette import status

from api.config import settings
from api.exception.internal_server_error import InternalServerErrorException
from api.exception.not_found import NotFoundException
from api.user.serializer.request.login import LoginUser
from api.user.service.user_service import login_user
from api.utils.response_utils import (
    ok_response,
    error_response,
)

router = APIRouter(
    prefix=f'{settings.route}/login',
    tags=['login'],
)


@router.post('')
async def login(data: LoginUser = Body(...)):
    try:
        response = login_user(data)
        return ok_response(
            message='Successfully logged in!',
            **{'data': response.get('login').dict()},
            status_code=status.HTTP_200_OK,
        )
    except (NotFoundException, InternalServerErrorException) as e:
        return error_response(message=e.message, status_code=e.status_code)
