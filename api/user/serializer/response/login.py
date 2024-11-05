from pydantic import BaseModel


class Login(BaseModel):
    id: int
    username: str
    access_token: str
    refresh_token: str
