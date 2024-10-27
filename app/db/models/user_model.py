from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .. import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, autoincrement=True
    )
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    profile_photo: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(String(300), nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    creation_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
