from typing import List

from sqlalchemy.orm import Session

from api.apartment.model.apartment_entity import Apartment


def find_apartment_by_name(session: Session, name: str) -> Apartment | None:
    return session.query(Apartment).filter(Apartment.name == name).first()


def find_apartments_by_user_id(session: Session, user_id: int) -> List[Apartment]:
    return session.query(Apartment).filter(Apartment.user_id == user_id).all()


def get_apartment_by_id(session: Session, user_id: int, apartment_id: int) -> Apartment | None:
    return session.query(Apartment).filter(Apartment.id == apartment_id, Apartment.user_id == user_id).first()
