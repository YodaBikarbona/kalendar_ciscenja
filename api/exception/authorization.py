from starlette.requests import Request
from starlette.responses import JSONResponse

from api.app import app


class AuthorizationException(Exception):

    def __init__(self, message: str = "Invalid credentials!"):
        super().__init__('Unauthorized!')
        self.message = message
        self.status_code = 401


@app.exception_handler(AuthorizationException)
async def bad_request_exception_handler(request: Request, exc: AuthorizationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
