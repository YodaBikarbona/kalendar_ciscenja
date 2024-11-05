from pydantic import (
    BaseModel,
    HttpUrl,
)


class NewCalendarFromUrl(BaseModel):
    url: HttpUrl
