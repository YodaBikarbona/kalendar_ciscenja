from datetime import date
from io import StringIO
from typing import (
    List,
    Dict,
    Any,
)

import httpx
from fastapi import (
    UploadFile,
    File,
)
from ics import (
    Calendar as Cal,
    Event as Ev,
)

from api.apartment.repository.apartment_repository import get_apartment_by_id
from api.base.database_connector import Session
from api.calendar.mapper.calendar_mapper import (
    calendar_mapper,
    event_mapper,
)
from api.calendar.model.calendar_entity import Calendar
from api.calendar.model.event_entity import Event
from api.calendar.repository.calendar_repository import (
    find_calendar_in_range_or_all,
    find_calendar_by_id,
    find_calendar_by_url,
    find_calendar_by_apartment_id,
)
from api.calendar.serializer.request.calendar import NewCalendarFromUrl
from api.exception.bad_request import BadRequestException
from api.exception.error_messages import (
    INVALID_CALENDAR_DATA,
    CALENDAR_HAS_NO_EVENTS,
    IMPORTING_CALENDAR_DATA_FAILED,
    FETCHING_CALENDARS_INTERNAL_SERVER_ERROR,
    CALENDAR_NOT_FOUND,
    CALENDAR_HAS_NO_EVENTS_TO_EXPORT,
    EXPORTING_CALENDAR_DATA_FAILED,
    APARTMENT_NOT_FOUND,
)
from api.exception.internal_server_error import InternalServerErrorException
from api.exception.not_found import NotFoundException
from api.logger.logger import logger
from api.utils.file_utils import (
    is_format_valid,
    read_ics_file,
)


async def upload_calendar(user_id: int, apartment_id: int, file: UploadFile = File(...)):
    is_format_valid(filename=file.filename)
    events_count = 0
    with Session.begin() as session:
        try:
            apartment = get_apartment_by_id(session=session, user_id=user_id, apartment_id=apartment_id)
            if not apartment:
                raise NotFoundException(APARTMENT_NOT_FOUND)
            calendar = None
            file_content = await file.read()
            for data in read_ics_file(file_content):
                if data.get('wrong_data'):
                    raise BadRequestException(INVALID_CALENDAR_DATA)
                if not calendar:
                    calendar = find_calendar_by_apartment_id(session=session, apartment_id=apartment_id,
                                                             user_id=user_id)
                    if not calendar:
                        calendar = calendar_mapper(apartment=apartment, data=data)
                        session.add(calendar)
                        session.flush()
                    else:
                        calendar = calendar_mapper(apartment=apartment, data=data, calendar=calendar)
                        calendar.events.clear()
                session.add(event_mapper(calendar=calendar, data=data))
                events_count += 1
            if events_count == 0:
                raise BadRequestException(CALENDAR_HAS_NO_EVENTS)
        except BadRequestException as e:
            session.rollback()
            logger.error(INVALID_CALENDAR_DATA, e)
            raise e
        except Exception as e:
            session.rollback()
            logger.error(IMPORTING_CALENDAR_DATA_FAILED, e)
            raise InternalServerErrorException()


def get_calendars(user_id: int, date_from: date | None, date_to: date | None) -> Dict[str, Any]:
    with Session.begin() as session:
        try:
            events = find_calendar_in_range_or_all(session=session, user_id=user_id, begin=date_from, end=date_to)
            if events:
                return make_calendar_structure(events=events, date_from=date_from, date_to=date_to)
        except Exception as e:
            session.rollback()
            logger.error(FETCHING_CALENDARS_INTERNAL_SERVER_ERROR, e)
            raise InternalServerErrorException()


def make_calendar_structure(events: List[Event], date_from: date | None, date_to: date | None) -> Dict[str, Any]:
    date_range = set()
    data = []
    calendars = set()
    apartments = sorted(list(set([event.calendar.apartment.get_name() for event in events])))
    for event in events:
        data.append({
            'id': event.calendar.id,
            'name': event.calendar.apartment.name,
            'url': event.calendar.url,
            'event_id': event.id,
            'begin': event.begin,
            'end': event.end,
            'summary': event.summary,
        })
        date_range.add(event.begin.date())
        calendars.add(event.calendar.name)
        if event.end:
            date_range.add(event.end.date())
    if date_from and date_to:
        date_range = [d for d in date_range if date_from <= d <= date_to]
    elif date_from:
        date_range = [d for d in date_range if date_from <= d]
    elif date_to:
        date_range = [d for d in date_range if date_to >= d]
    date_range = sorted(date_range)
    return group_data(dates=date_range, apartments=apartments, data=data)


def group_data(dates: List[date], apartments: List[str], data: List[Dict[str, Any]]) -> Dict[str, Any]:
    grouped_data = []
    cleaned_events = []
    taken_events = []
    free_events = []
    begin_before_range = {d.get('name'): True for d in data if d.get('begin').date() < min(dates)}
    end_before_range = {d.get('name'): True for d in data if d.get('end').date() < min(dates)}
    for single_date in dates:
        events_in_range = [
            make_event_structure(_date=single_date, data=d)
            for d in data
            if d.get('begin').date() == single_date or (d.get('end') and d.get('end').date() == single_date)
        ]
        predict_cleaning(events=events_in_range, cleaned_events=cleaned_events)
        cleaned_events = [s.get('name') for s in events_in_range if s.get('cleaning')]
        remove_cleaned_events(events=events_in_range, cleaned_events=cleaned_events)
        update_begin_and_before_range(events=events_in_range, begin_before_range=begin_before_range,
                                      end_before_range=end_before_range)
        make_as_free(events=events_in_range, apartments=apartments, end_before_range=end_before_range,
                     free_events=free_events, taken_events=taken_events, begin_before_range=begin_before_range)
        free_events = [event.get('name') for event in events_in_range if event.get('end') and event.get('free')]
        make_as_taken(events=events_in_range, apartments=apartments, begin_before_range=begin_before_range,
                      taken_events=taken_events, free_events=free_events, end_before_range=end_before_range)
        taken_events = [event.get('name') for event in events_in_range if event.get('begin') and event.get('taken')]
        grouped_data.append([
            {**event, 'date': event['date'].strftime("%Y-%m-%d")} for event in events_in_range
        ])
    return {
        'dates': [d.strftime("%Y-%m-%d") for d in sorted(dates)],
        'apartments': apartments,
        'events': grouped_data,
    }


def make_as_free(apartments: List[str], free_events: List[str], end_before_range: Dict[str, Any],
                 events: List[Dict[str, Any]], taken_events: List[str], begin_before_range: Dict[str, Any]):
    event_names = {event.get('name'): True for event in events}
    for apartment in apartments:
        _free = False
        if end_before_range.get(apartment):
            _free = True
        elif event_names.get(apartment):
            continue
        elif apartment in free_events:
            _free = True
        elif apartment not in taken_events and apartment not in begin_before_range:
            _free = True
        if _free:
            event = make_event_structure(_date=events[0].get('date'),
                                         data={'name': apartment, 'taken': False, 'free': True})
            events.append(event)


def make_as_taken(apartments: List[str], taken_events: List[str], begin_before_range: Dict[str, Any],
                  events: List[Dict[str, Any]], free_events: List[str], end_before_range: Dict[str, Any]):
    event_names = {event.get('name'): True for event in events}
    for apartment in apartments:
        _taken = False
        if begin_before_range.get(apartment):
            _taken = True
        elif event_names.get(apartment):
            continue
        elif apartment in taken_events:
            _taken = True
        elif apartment not in free_events and apartment not in end_before_range:
            _taken = True
        if _taken:
            event = make_event_structure(_date=events[0].get('date'),
                                         data={'name': apartment, 'taken': True, 'free': False})
            events.append(event)


def update_begin_and_before_range(events: List[Dict[str, Any]], begin_before_range: Dict[str, Any],
                                  end_before_range: Dict[str, Any]):
    for event in events:
        if begin_before_range.get(event.get('name')) and event.get('end'):
            del begin_before_range[event.get('name')]
        if end_before_range.get(event.get('name')) and event.get('begin'):
            del end_before_range[event.get('name')]


def make_event_structure(_date: date, data: Dict[str, Any]) -> Dict[str, Any]:
    begin = data.get('begin').date() == _date if data.get('begin') else None
    end = data.get('end').date() == _date if data.get('end') else None
    taken = begin if begin else data.get('taken', False)
    free = end if end else data.get('free', False)
    return {
        'date': _date,
        'name': data.get('name'),
        'begin': begin,
        'end': end,
        'taken': taken,
        'free': free,
        'cleaning': False,
    }


def remove_as_free(events: List[Dict[str, Any]], free_events: List[str]):
    remove_free_events = [event.get('name') for event in events if
                          event.get('name') not in free_events and event.get('end')]
    free_events[:] = [name for name in free_events if name not in remove_free_events]


def remove_as_taken(events: List[Dict[str, Any]], taken_events: List[str]):
    remove_taken_events = [event.get('name') for event in events if
                           event.get('name') in taken_events and event.get('end')]
    taken_events[:] = [name for name in taken_events if name not in remove_taken_events]


def predict_cleaning(events: List[Dict[str, Any]], cleaned_events: List[str]):
    _names = list(set([e.get('name') for e in events]))
    for name in set(_names):
        event_begin = [e for e in events if e.get('name') == name and e.get('begin')]
        event_end = [e for e in events if e.get('name') == name and e.get('end')]
        if len(event_end) > 0 and len(event_begin) == 0:
            update_cleaning(events=events, cleaned_events=cleaned_events, target_name=name)
        elif len(event_end) > 0 and len(event_begin) > 0:
            for e in event_end:
                e['cleaning'] = True


def remove_cleaned_events(events: List[Dict[str, Any]], cleaned_events: List[str]):
    _names = list(set([e.get('name') for e in events]))
    remove_events = []
    for name in set(_names):
        event_begin = [e for e in events if e.get('name') == name and e.get('begin')]
        event_end = [e for e in events if e.get('name') == name and e.get('end')]
        if len(event_end) > 0 and len(event_begin) > 0:
            for _ in event_begin:
                remove_events.append(name)
    if remove_events:
        cleaned_events[:] = [name for name in cleaned_events if name not in remove_events]


def update_cleaning(events: List[Dict[str, Any]], cleaned_events: List[str], target_name: str):
    for event in events:
        if event.get('name') == target_name and event.get('name') not in cleaned_events:
            event['cleaning'] = True
            cleaned_events.append(event.get('name'))


def download_calendar(user_id: int, calendar_id: int):
    with Session.begin() as session:
        try:
            calendar = find_calendar_by_id(session=session, user_id=user_id, _id=calendar_id)
            if not calendar:
                raise NotFoundException(CALENDAR_NOT_FOUND)
            if not calendar.events:
                raise BadRequestException(CALENDAR_HAS_NO_EVENTS_TO_EXPORT)
            cal = prepare_data_to_export(calendar=calendar)
            ics_data = StringIO()
            ics_data.writelines(cal.serialize_iter())
            ics_data.seek(0)
            return ics_data
        except NotFoundException as e:
            logger.error(CALENDAR_NOT_FOUND)
            raise e
        except BadRequestException as e:
            logger.error(CALENDAR_HAS_NO_EVENTS_TO_EXPORT)
            raise e
        except Exception as e:
            logger.error(EXPORTING_CALENDAR_DATA_FAILED, e)
            raise InternalServerErrorException()


def prepare_data_to_export(calendar: Calendar) -> Cal:
    cal = Cal()
    cal.creator = calendar.name
    cal.version = calendar.version
    cal.method = calendar.method
    cal.scale = calendar.scale
    for e in calendar.events:
        event = Ev()
        event.begin = e.begin
        event.end = e.end
        event.name = e.summary
        event.uid = e.uid
        cal.events.add(event)
    return cal


async def upload_calendar_from_url(user_id: int, apartment_id: int, data: NewCalendarFromUrl):
    is_format_valid(url=data.url)
    events_count = 0
    with (Session.begin() as session):
        try:
            apartment = get_apartment_by_id(session=session, user_id=user_id, apartment_id=apartment_id)
            if not apartment:
                raise NotFoundException(APARTMENT_NOT_FOUND)
            calendar = None
            file_content = await get_remote_data(str(data.url))
            for d in read_ics_file(file_content):
                if d.get('wrong_data'):
                    raise BadRequestException(INVALID_CALENDAR_DATA)
                if not calendar:
                    calendar =find_calendar_by_url(
                        session=session, url=str(data.url), apartment_id=apartment_id,user_id=user_id) or\
                              find_calendar_by_apartment_id(session=session, apartment_id=apartment_id, user_id=user_id)
                    if not calendar:
                        calendar = calendar_mapper(apartment=apartment, data=d, url=str(data.url))
                        session.add(calendar)
                        session.flush()
                    else:
                        calendar = calendar_mapper(apartment=apartment, data=d, calendar=calendar, url=str(data.url))
                        calendar.events.clear()
                session.add(event_mapper(calendar=calendar, data=d))
                events_count += 1
            if events_count == 0:
                raise BadRequestException(CALENDAR_HAS_NO_EVENTS)
        except BadRequestException as e:
            session.rollback()
            logger.error(INVALID_CALENDAR_DATA, e)
            raise e
        except Exception as e:
            session.rollback()
            logger.error(IMPORTING_CALENDAR_DATA_FAILED, e)
            raise InternalServerErrorException()


async def get_remote_data(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        file_content = response.content
    return file_content
