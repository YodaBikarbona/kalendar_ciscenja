from pydantic import (
    BaseModel,
    Field,
)


class NewApartment(BaseModel):
    name: str = Field(min_length=3, max_length=64)
