from api.base.database_connector import Session
from api.user.model.user_entity import User


def find_user_by_username(session: Session, username: str) -> User:
    return session.query(User).filter(User.username == username).first()


def find_user_by_id(session: Session, user_id: int) -> User:
    return session.query(User).filter(User.id == user_id).first()
