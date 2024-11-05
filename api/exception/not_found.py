from starlette.requests import Request
from starlette.responses import JSONResponse

from api.app import app


class NotFoundException(Exception):

    def __init__(self, message: str):
        super().__init__('Not Found')
        self.message = message
        self.status_code = 404


@app.exception_handler(NotFoundException)
async def bad_request_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
