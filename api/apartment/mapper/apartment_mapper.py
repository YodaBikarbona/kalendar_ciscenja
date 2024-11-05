from typing import (
    List,
    Dict,
    Any,
)

from api.apartment.model.apartment_entity import Apartment
from api.apartment.serializer.request.apartment import NewApartment
from api.apartment.serializer.response.apartment import Apartment as ApartmentSerializer
from api.user.model.user_entity import User


def apartment_mapper(data: NewApartment, user: User) -> Apartment:
    apartment = Apartment(user=user)
    apartment.set_name(data.name)
    return apartment


def apartment_entities_to_apartments_serializer(apartments: List[Apartment]) -> List[Dict[str, Any]]:
    return [
        ApartmentSerializer(
            id=apartment_entity.get_id(),
            name=apartment_entity.get_name(),
            user_id=apartment_entity.get_user_id()
        ).model_dump() for apartment_entity in apartments]
