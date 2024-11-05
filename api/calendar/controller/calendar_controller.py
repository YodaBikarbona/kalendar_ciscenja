from datetime import date
from typing import Optional

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    Query,
)
from starlette import status
from starlette.responses import StreamingResponse

from api.calendar.serializer.request.calendar import NewCalendarFromUrl
from api.calendar.service.calendar_service import (
    upload_calendar,
    get_calendars,
    download_calendar,
    upload_calendar_from_url,
)
from api.config import settings
from api.exception.bad_request import BadRequestException
from api.exception.internal_server_error import InternalServerErrorException
from api.exception.not_found import NotFoundException
from api.utils.jwt_utils import get_current_user_id
from api.utils.response_utils import (
    ok_response,
    error_response,
)

router = APIRouter(
    prefix=f'{settings.route}/calendars',
    tags=['calendars'],
)


@router.get('')
async def calendars(
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user_id: int = Depends(get_current_user_id)):
    try:
        data = get_calendars(user_id=user_id, date_from=date_from, date_to=date_to)
        return ok_response(
            message='Calendars.',
            status_code=status.HTTP_200_OK,
            **{'data': data}
        )
    except InternalServerErrorException as e:
        return error_response(message=e.message, status_code=e.status_code)


@router.post('/apartments/{apartment_id}/import')
async def import_calendar(
        apartment_id: int,
        file: UploadFile = File(...),
        user_id: int = Depends(get_current_user_id)):
    try:
        await upload_calendar(file=file, user_id=user_id, apartment_id=apartment_id)
        return ok_response(
            message='Calendar has successfully uploaded!',
            status_code=status.HTTP_201_CREATED,
        )
    except (BadRequestException, InternalServerErrorException) as e:
        return error_response(message=e.message, status_code=e.status_code)


@router.get('/{calendar_id}/export')
async def export_calendar(calendar_id: int, user_id: int = Depends(get_current_user_id)):
    try:
        data = download_calendar(calendar_id=calendar_id, user_id=user_id)
        return StreamingResponse(
            data,
            media_type="text/calendar",
            headers={
                "Content-Disposition": "attachment; filename=calendar_export.ics"
            }
        )
    except (NotFoundException, BadRequestException, InternalServerErrorException) as e:
        return error_response(message=e.message, status_code=e.status_code)


@router.post("/apartments/{apartment_id}/import-from-url")
async def import_from_url(apartment_id: int, data: NewCalendarFromUrl, user_id: int = Depends(get_current_user_id)):
    try:
        await upload_calendar_from_url(user_id=user_id, apartment_id=apartment_id, data=data)
        return ok_response(
            message='Calendar from the has successfully uploaded!',
            status_code=status.HTTP_201_CREATED,
        )
    except (BadRequestException, InternalServerErrorException) as e:
        return error_response(message=e.message, status_code=e.status_code)
