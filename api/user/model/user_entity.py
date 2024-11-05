from hashlib import sha512

from sqlalchemy import (
    Column,
    Unicode,
    UniqueConstraint,
    Sequence,
    event,
)
from sqlalchemy.orm import relationship

from api.base.database_connector import (
    Base,
    engine,
)
from api.base.model.base_entity import BaseEntity
from api.exception.internal_server_error import InternalServerErrorException
from api.utils.utils import generate_random_string


class User(BaseEntity):
    __tablename__ = 'users'

    # Columns
    username = Column(Unicode(32), nullable=False, unique=True, name='username')
    password = Column(Unicode(128), nullable=False, name='password')
    salt = Column(Unicode(255), nullable=False, name='salt')

    # Relationships
    apartments = relationship("Apartment", back_populates="user")

    # Constraints
    UniqueConstraint(username, name="unique_username")

    def __str__(self):
        return f"UserID: {self.get_id()}, username: {self.get_username()}"

    def __encrypt_psw(self, password_row: str) -> str:
        return sha512(f'{password_row}{self.salt}'.encode('utf-8')).hexdigest()

    def is_password_valid(self, password_row: str) -> bool:
        return self.__encrypt_psw(password_row) == self.password

    def get_username(self):
        return self.username

    def set_username(self, value: str):
        self.username = value

    def set_password(self, value: str):
        self.password = value

    def get_apartments(self):
        return self.apartments


@event.listens_for(User, "before_insert")
def encrypt_password_before_insert(mapper, connect, target):
    if not target.password:
        raise InternalServerErrorException()
    target.salt = generate_random_string()
    target.password = target._User__encrypt_psw(target.password)


User.__table__.columns['id'].sequence = Sequence('user_id_seq')
Base.metadata.create_all(engine)
