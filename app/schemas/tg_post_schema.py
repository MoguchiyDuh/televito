from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class ShortTGPostSchema(BaseModel):
    id: int
    location: str
    price: float
    status: date
    publication_datetime: datetime
    first_image: Optional[str] = None

    @classmethod
    def from_orm_model(cls, orm_model):
        images_list = orm_model.images or []
        first_image = images_list[0] if images_list else None
        return cls.model_construct(
            id=orm_model.id,
            location=orm_model.location,
            price=orm_model.price,
            status=orm_model.status,
            publication_datetime=orm_model.publication_datetime,
            first_image=first_image,
        )


class TGPostSchema(BaseModel):
    google_maps_url: str
    location: str
    status: Optional[date]
    price: float
    duration: Optional[int]
    is_new: Optional[bool]
    rooms: Optional[float]
    room_description: Optional[str]
    area: Optional[float]
    floor: Optional[int]
    floors_in_building: Optional[int]
    pets_allowed: Optional[bool]
    parking: Optional[str]
    images: list[str]
    publication_datetime: datetime
