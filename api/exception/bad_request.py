from starlette.requests import Request
from starlette.responses import JSONResponse

from api.app import app


class BadRequestException(Exception):

    def __init__(self, message: str):
        super().__init__('Bad Request')
        self.message = message
        self.status_code = 400


@app.exception_handler(BadRequestException)
async def bad_request_exception_handler(request: Request, exc: BadRequestException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
