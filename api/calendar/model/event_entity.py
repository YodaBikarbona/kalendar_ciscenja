import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Column,
    Unicode,
    Integer,
    ForeignKey,
    Sequence,
    TIMESTAMP,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from api.base.database_connector import (
    Base,
    engine,
)
from api.base.model.base_entity import BaseEntity
from api.calendar.model.calendar_entity import Calendar


class Event(BaseEntity):
    __tablename__ = 'events'

    # Columns
    begin = Column(TIMESTAMP(timezone=True), nullable=False, name='begin')
    end = Column(TIMESTAMP(timezone=True), nullable=True, name='end')
    summary = Column(Unicode(64), nullable=False, name='summary')
    uid = Column(Unicode(64), nullable=False, name='uid', default=lambda: str(uuid.uuid4()))

    # Private Foreign Key
    calendar_id = Column(Integer, ForeignKey('calendars.id'), nullable=False, name='calendar_id')

    UniqueConstraint('calendar_id', 'begin', name='unique_calendar_id_begin')

    # Relationships
    calendar = relationship("Calendar", back_populates="events")

    def __init__(self, calendar: Calendar, **kw: Any):
        super().__init__(**kw)
        self.calendar = calendar
        self.calendar_id = calendar.id

    def get_begin(self):
        return self.begin

    def set_begin(self, value: datetime):
        self.begin = value

    def get_end(self):
        return self.end

    def set_end(self, value: datetime):
        self.end = value

    def get_summary(self):
        return self.summary

    def set_summary(self, value: str):
        self.summary = value

    def get_calendar_id(self):
        return self.calendar_id

    def get_calendar(self):
        return self.calendar

    def set_calendar(self, value: Calendar):
        self.calendar = value

    def set_uid(self, value: str):
        self.uid = value

    def get_uid(self):
        return self.uid


Event.__table__.columns['id'].sequence = Sequence('event_id_seq')
Base.metadata.create_all(engine)
