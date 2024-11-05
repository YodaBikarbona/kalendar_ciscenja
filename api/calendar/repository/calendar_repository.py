from datetime import (
    date,
    timedelta,
)
from typing import List

from api.apartment.model.apartment_entity import Apartment
from api.base.database_connector import Session
from api.calendar.model.calendar_entity import Calendar
from api.calendar.model.event_entity import Event


def find_calendar_by_name(session: Session, name: str) -> Calendar:
    return session.query(Calendar).filter(Calendar.name == name).first()


def find_calendar_by_url(session: Session, url: str, apartment_id: int, user_id: int) -> Calendar:
    return session.query(Calendar) \
        .join(Calendar.apartment) \
        .filter(Calendar.url == url, Calendar.apartment_id == apartment_id, Apartment.user_id == user_id).first()


def find_calendar_by_id(session: Session, _id: int, user_id: int) -> Calendar:
    return session.query(Calendar) \
        .join(Calendar.apartment).filter(Calendar.id == _id, Apartment.user_id == user_id).first()


def find_calendar_in_range_or_all(session: Session, user_id: int, begin: date | None, end: date | None) -> List[Event]:
    base_query = session.query(Event) \
        .join(Calendar.apartment) \
        .join(Calendar.events) \
        .filter(Apartment.user_id == user_id)
    if begin and end:
        base_query = base_query.filter(
            (Event.begin.between(begin, end + timedelta(days=1))) | Event.end.between(begin, end + timedelta(days=1)))
    elif begin:
        base_query = base_query.filter((Event.begin >= begin) | (Event.end >= begin))
    elif end:
        base_query = base_query.filter(
            (Event.begin <= end + timedelta(days=1)) |
            (Event.end <= end + timedelta(days=1))
        )
    return base_query.order_by(Event.begin, Event.id).all()


def find_calendar_by_apartment_id(session: Session, apartment_id: int, user_id: int) -> Calendar:
    return session.query(Calendar) \
        .join(Calendar.apartment) \
        .filter(Calendar.apartment_id == apartment_id, Apartment.user_id == user_id).first()
