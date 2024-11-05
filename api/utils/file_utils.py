from datetime import (
    datetime,
    time,
)
from typing import (
    Generator,
    Dict,
)

from ics import Calendar
from pydantic import HttpUrl

from api.exception.bad_request import BadRequestException
from api.exception.error_messages import INVALID_CALENDAR_DATA


def read_ics_file(file_content: bytes) -> Generator[Dict[str, str | datetime], None, None]:
    """
    The function will process the file and make event structure.
    :param file_content:
    :return: Generator[Dict[str, str | datetime], None, None]
    """
    decoded_content = file_content.decode("utf-8")
    calendar = Calendar(decoded_content)

    for event in calendar.events:

        wrong_data = False
        begin = datetime.strptime(event.begin.isoformat(), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)
        end = datetime.strptime(event.end.isoformat(), '%Y-%m-%dT%H:%M:%S%z').replace(
            tzinfo=None) if event.end else None

        if begin > end or begin.time() > time(15, 0) or (end and end.time() > time(11, 0)):
            wrong_data = True

        yield {
            'version': calendar.version,
            'method': calendar.method,
            'scale': calendar.scale,
            'wrong_data': wrong_data,
            'calendar_name': calendar.creator,
            'summary': event.name,
            'begin': begin,
            'end': end,
            'description': event.description,
            'location': event.location,
            'uid': event.uid,
        }


def is_format_valid(filename: str = '', url: HttpUrl = None):
    """
    The method will check is the file .ics extension or is the url .ics extension.
    Any of these types should be calendar file.
    :param filename:
    :param url:
    :raise: BadRequestException
    """
    if (url and url.path.endswith('.ics')) or (filename and filename.endswith('.ics')):
        return
    raise BadRequestException(INVALID_CALENDAR_DATA)
