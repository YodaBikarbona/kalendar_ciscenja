from api.base.database_connector import Session
from api.exception.bad_request import BadRequestException
from api.exception.internal_server_error import InternalServerErrorException
from api.logger.logger import logger
from api.user.mapper.user_mapper import (
    mapper_new_user_to_user,
    mapper_user_to_login,
)
from api.user.repository.user_repository import find_user_by_username
from api.user.serializer.request.login import LoginUser
from api.user.serializer.request.register import NewUser


def register_user(new_user: NewUser):
    with Session.begin() as session:
        try:
            user = find_user_by_username(session=session, username=new_user.username)
            if user:
                logger.info("User already exists!")
                raise BadRequestException('User already exists!')
            user = mapper_new_user_to_user(new_user=new_user)
            session.add(user)
            logger.info(f'New user registered: ID: {user.get_id()}, username: {new_user.username}')
        except BadRequestException as e:
            raise e
        except Exception as e:
            session.rollback()
            logger.error(f'The registration of the new user failed, username:{new_user.username}', e)
            raise InternalServerErrorException()


def login_user(data: LoginUser) -> dict:
    with Session.begin() as session:
        try:
            user = find_user_by_username(session=session, username=data.username)
            if not user or (user and not user.is_password_valid(data.password)):
                logger.info("User does not exist or password is invalid!")
                raise BadRequestException("Invalid credentials!")
            return {
                'login': mapper_user_to_login(user=user),
            }
        except BadRequestException as e:
            raise e
        except Exception as e:
            session.rollback()
            logger.error(f'The login of the new user failed, username:{data.username}', e)
            raise InternalServerErrorException()
