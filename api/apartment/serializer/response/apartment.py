from pydantic import BaseModel


class Apartment(BaseModel):
    id: int
    name: str
    user_id: int
