from typing import (
    List,
    Dict,
    Any,
)

from api.apartment.mapper.apartment_mapper import (
    apartment_mapper,
    apartment_entities_to_apartments_serializer,
)
from api.apartment.repository.apartment_repository import (
    find_apartment_by_name,
    find_apartments_by_user_id,
)
from api.apartment.serializer.request.apartment import NewApartment
from api.base.database_connector import Session
from api.exception.bad_request import BadRequestException
from api.exception.error_messages import (
    APARTMENT_ALREADY_EXIST,
    CREATING_APARTMENT_INTERNAL_SERVER_ERROR,
    APARTMENTS_NOT_FOUND,
)
from api.exception.internal_server_error import InternalServerErrorException
from api.exception.not_found import NotFoundException
from api.logger.logger import logger
from api.user.repository.user_repository import find_user_by_id


def create_new_apartment(user_id: int, data: NewApartment):
    with Session.begin() as session:
        try:
            apartment = find_apartment_by_name(session=session, name=data.name)
            if apartment:
                raise BadRequestException(APARTMENT_ALREADY_EXIST)
            apartment = apartment_mapper(data=data, user=find_user_by_id(session=session, user_id=user_id))
            session.add(apartment)
            logger.info(f'New apartment created: UID: {user_id}, apartment name: {apartment.name}')
        except BadRequestException as e:
            logger.exception(e)
            raise e
        except Exception as e:
            logger.error(CREATING_APARTMENT_INTERNAL_SERVER_ERROR, e)
            raise InternalServerErrorException()


def get_all_apartments(user_id: int) -> List[Dict[str, Any]]:
    with Session.begin() as session:
        try:
            apartments = find_apartments_by_user_id(session=session, user_id=user_id)
            if not apartments:
                raise NotFoundException(APARTMENTS_NOT_FOUND)
            return apartment_entities_to_apartments_serializer(apartments=apartments)
        except NotFoundException as e:
            logger.exception(e)
            raise e
        except Exception as e:
            logger.error(CREATING_APARTMENT_INTERNAL_SERVER_ERROR, e)
            raise InternalServerErrorException()
