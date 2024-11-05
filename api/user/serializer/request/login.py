from pydantic import (
    BaseModel,
    Field,
)


class LoginUser(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)
