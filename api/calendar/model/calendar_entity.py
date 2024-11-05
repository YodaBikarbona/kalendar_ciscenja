from typing import Any

from sqlalchemy import (
    Column,
    Unicode,
    Integer,
    ForeignKey,
    Sequence,
)
from sqlalchemy.orm import relationship

from api.apartment.model.apartment_entity import Apartment
from api.base.database_connector import (
    Base,
    engine,
)
from api.base.model.base_entity import BaseEntity


class Calendar(BaseEntity):
    __tablename__ = 'calendars'

    # Columns
    name = Column(Unicode(255), nullable=False, unique=True, name='name')
    url = Column(Unicode(255), nullable=True, name='url')
    scale = Column(Unicode(32), nullable=False, name='scale', default='gregorian')
    method = Column(Unicode(32), nullable=False, name='method', default='publish')
    version = Column(Unicode(8), nullable=False, name='version', default='1.0')

    # Private Foreign Key
    apartment_id = Column(Integer, ForeignKey('apartments.id'), nullable=False, unique=True, name='apartment_id')

    # Relationships
    apartment = relationship("Apartment", back_populates="calendar", uselist=False)
    events = relationship("Event", back_populates="calendar", cascade="all, delete-orphan")

    def __init__(self, apartment: Apartment, **kw: Any):
        super().__init__(**kw)
        self.apartment = apartment
        self.apartment_id = apartment.id

    def get_name(self):
        return self.name

    def set_name(self, value: str):
        self.name = value

    def get_url(self):
        return self.url

    def set_url(self, value: str):
        self.url = value

    def get_scale(self):
        return self.scale

    def set_scale(self, value: str):
        self.scale = value

    def get_method(self):
        return self.method

    def set_method(self, value: str):
        self.method = value

    def get_version(self):
        return self.version

    def set_version(self, value: str):
        self.version = value

    def get_apartment_id(self):
        return self.apartment_id

    def get_apartment(self):
        return self.apartment


Calendar.__table__.columns['id'].sequence = Sequence('calendar_id_seq')
Base.metadata.create_all(engine)
