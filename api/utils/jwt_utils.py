from datetime import timedelta
from typing import Any

from fastapi import Depends
from fastapi.security import HTTPBearer
from jose import jwt

from api.base.database_connector import Session
from api.config import settings
from api.exception.authorization import AuthorizationException
from api.exception.internal_server_error import InternalServerErrorException
from api.logger.logger import logger
from api.user.model.user_entity import User
from api.user.repository.user_repository import find_user_by_id
from api.utils.utils import now

bearer_scheme = HTTPBearer()


def generate_token(user: User, is_access: bool = True):
    """
    The function will encode the security token that the client side will send
    in every request inside the header.
    :param user:
    :param is_access:
    :return: encoded_token (str)
    """
    if is_access:
        expiration_date = now() + timedelta(minutes=5)
        secret = settings.jwt_access_secret_key
    else:
        expiration_date = now() + timedelta(days=30)
        secret = settings.jwt_refresh_secret_key
    return jwt.encode(
        {
            'user_id': user.get_id(),
            'exp': expiration_date,
        }, secret, algorithm='HS256')


def decode_token(token: str, is_access: bool = True) ->  dict[str, Any]:
    """
    The function will decode the security token that the client side will send
    in every request inside the header.
    :param token:
    :param is_access:
    :return: decoded_token: dict[str, Any]
    :raise: AuthorizationException or AuthorizationException
    """
    if is_access:
        secret = settings.jwt_access_secret_key
    else:
        secret = settings.jwt_refresh_secret_key
    try:
        return jwt.decode(token, secret, algorithms='HS256')
    except jwt.ExpiredSignatureError:
        logger.info(f'Signature expired. {token}')
        raise AuthorizationException('Signature expired!') \
            if is_access else AuthorizationException('Signature expired, please log in again!')
    except Exception as e:
        logger.info('Something is wrong with security-token!', e)
        raise AuthorizationException()


def get_current_user_id(token: str = Depends(bearer_scheme)) -> int:
    """
    The function will check and get the user that will be forwarded into endpoint
    :param token:
    :return: user_id: int
    :raise: AuthorizationException or InternalServerErrorException
    """
    with Session.begin() as session:
        try:
            payload = decode_token(token.credentials)
            user_id: int = payload.get("user_id")
            if not (user_id or user_id and find_user_by_id(session=session, user_id=user_id)):
                raise AuthorizationException()
            return user_id
        except AuthorizationException as e:
            raise e
        except Exception as e:
            logger.error('Something is wrong with security-token! %s', e)
            raise InternalServerErrorException()
