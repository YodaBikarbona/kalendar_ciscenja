from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from api.config import settings

from api.logger.logger import logger
from api.utils.response_utils import ok_response

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(f"{settings.route}")
async def server_liveness():
    """
    Server liveness probe.
    Used by automated tools to check that the server is online.
    """
    return ok_response(message="The Rest server is alive!")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Server is shutting down!")


@app.on_event("startup")
async def startup():
    logger.info("Server is starting up!")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html") as file:
        return HTMLResponse(content=file.read(), status_code=200)
