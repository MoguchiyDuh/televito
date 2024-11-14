from datetime import datetime
from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column
from .. import Base


class TGPostModel(Base):
    __tablename__ = "tg_posts"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, autoincrement=True
    )
    google_maps_url: Mapped[str] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[datetime] = mapped_column(Date, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)  # Euro
    duration: Mapped[int] = mapped_column(
        Integer, nullable=True
    )  # minimal lease duration in months
    is_new: Mapped[bool] = mapped_column(Boolean, nullable=True)
    rooms: Mapped[float] = mapped_column(Float, nullable=True)
    room_description: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # total floors in a building
    area: Mapped[float] = mapped_column(Float, nullable=True)
    floor: Mapped[int] = mapped_column(Integer, nullable=True)
    floors_in_building: Mapped[int] = mapped_column(Integer, nullable=True)
    pets_allowed: Mapped[bool] = mapped_column(Boolean, nullable=True)
    parking: Mapped[str] = mapped_column(String(100), nullable=True)
    images: Mapped[list[str]] = mapped_column(ARRAY(String(100)), nullable=True)
    publication_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
