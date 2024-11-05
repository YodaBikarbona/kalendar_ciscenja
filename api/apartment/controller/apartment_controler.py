from fastapi import (
    APIRouter,
    Body,
    Depends,
)
from starlette import status

from api.apartment.serializer.request.apartment import NewApartment
from api.apartment.service.apartment_service import (
    create_new_apartment,
    get_all_apartments,
)
from api.config import settings
from api.exception.bad_request import BadRequestException
from api.exception.internal_server_error import InternalServerErrorException
from api.exception.not_found import NotFoundException
from api.utils.jwt_utils import get_current_user_id
from api.utils.response_utils import (
    ok_response,
    error_response,
)

router = APIRouter(
    prefix=f'{settings.route}/apartments',
    tags=['apartments'],
)


@router.post('/new')
def new_apartment(
        data: NewApartment = Body(...),
        user_id: int = Depends(get_current_user_id)):
    try:
        create_new_apartment(data=data, user_id=user_id)
        return ok_response(
            message='Apartment has successfully created!',
            status_code=status.HTTP_201_CREATED,
        )
    except (BadRequestException, InternalServerErrorException) as e:
        return error_response(message=e.message, status_code=e.status_code)


@router.get('')
def all_apartments(user_id: int = Depends(get_current_user_id)):
    try:
        data = get_all_apartments(user_id=user_id)
        return ok_response(
            message='Apartments.',
            status_code=status.HTTP_200_OK,
            **{'data': data},
        )
    except (NotFoundException, InternalServerErrorException) as e:
        return error_response(message=e.message, status_code=e.status_code)
