from typing import (
    Any,
    Dict,
)

from api.apartment.model.apartment_entity import Apartment
from api.calendar.model.calendar_entity import Calendar
from api.calendar.model.event_entity import Event


def calendar_mapper(apartment: Apartment, data: Dict[str, Any], url: str = None, calendar: Calendar = None) -> Calendar:
    if not calendar:
        calendar = Calendar(apartment=apartment)
    calendar.set_name(value=data.get('calendar_name'))
    calendar.set_url(value=url)
    calendar.set_scale(value=data.get('scale') or calendar.get_scale())
    calendar.set_method(value=data.get('method') or calendar.get_method())
    calendar.set_version(value=data.get('version') or calendar.get_version())
    return calendar


def event_mapper(calendar: Calendar, data: dict[str, Any]) -> Event:
    event = Event(calendar=calendar)
    event.set_summary(value=data.get('summary'))
    event.set_begin(value=data.get('begin'))
    event.set_end(value=data.get('end'))
    event.set_uid(value=data.get('uid'))
    return event
