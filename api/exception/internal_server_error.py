from starlette.requests import Request
from starlette.responses import JSONResponse

from api.app import app


class InternalServerErrorException(Exception):

    def __init__(self):
        super().__init__('Internal Server Error')
        self.message = 'Something went wrong!'
        self.status_code = 500


@app.exception_handler(InternalServerErrorException)
async def bad_request_exception_handler(request: Request, exc: InternalServerErrorException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
