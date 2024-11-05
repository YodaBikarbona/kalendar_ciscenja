from typing import Any

from sqlalchemy import (
    Column,
    Unicode,
    Integer,
    ForeignKey,
    UniqueConstraint,
    Sequence,
)
from sqlalchemy.orm import relationship

from api.base.database_connector import (
    Base,
    engine,
)
from api.base.model.base_entity import BaseEntity
from api.user.model.user_entity import User


class Apartment(BaseEntity):
    __tablename__ = 'apartments'

    # Columns
    name = Column(Unicode(64), nullable=False, unique=True, name='name')

    # Private Foreign Key
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, name='user_id')

    # Relationships
    user = relationship("User", back_populates="apartments")
    calendar = relationship("Calendar", back_populates="apartment", uselist=False)

    # Constraints
    UniqueConstraint('name', 'user_id', name='unique_user_apartment_name')

    def __init__(self, user: User, **kw: Any):
        super().__init__(**kw)
        self.user = user
        self.user_id = user.id

    def get_name(self):
        return self.name

    def set_name(self, value: str):
        self.name = value

    def get_user_id(self):
        return self.user_id

    def get_user(self):
        return self.user


Apartment.__table__.columns['id'].sequence = Sequence('apartment_id_seq')
Base.metadata.create_all(engine)
