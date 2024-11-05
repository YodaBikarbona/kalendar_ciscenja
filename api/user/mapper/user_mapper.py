from api.user.model.user_entity import User
from api.user.serializer.request.register import NewUser
from api.user.serializer.response.login import Login
from api.utils.jwt_utils import generate_token


def mapper_new_user_to_user(new_user: NewUser) -> User:
    user = User()
    user.set_username(new_user.username)
    user.set_password(new_user.password)
    return user


def mapper_user_to_login(user: User) -> Login:
    access_token = generate_token(user=user)
    refresh_token = generate_token(user=user, is_access=False)
    return Login(id=user.get_id(), username=user.get_username(), access_token=access_token, refresh_token=refresh_token)
