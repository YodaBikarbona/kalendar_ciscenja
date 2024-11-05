from pydantic import (
    Field,
    BaseModel,
    model_validator,
)
from api.exception.bad_request import BadRequestException


class NewUser(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)
    confirm_password: str = Field(min_length=6)

    @model_validator(mode="before")
    def check_passwords_match(cls, values):
        if values.get('password') != values.get('confirm_password'):
            raise BadRequestException("Password and confirm password don't match")
        return values
