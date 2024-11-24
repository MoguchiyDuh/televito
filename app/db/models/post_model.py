from datetime import datetime
from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .. import Base


class PostModel(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, autoincrement=True
    )
    location: Mapped[str] = mapped_column(String(150), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_new: Mapped[bool] = mapped_column(Boolean, nullable=True)
    images: Mapped[list[str]] = mapped_column(ARRAY(String(100)), nullable=True)
    publication_datetime: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=False
    )
    subcategory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )

    author = relationship("UserModel", back_populates="posts")
    category = relationship(
        "CategoryModel", foreign_keys=[category_id], back_populates="posts"
    )
    subcategory = relationship(
        "CategoryModel", foreign_keys=[subcategory_id], back_populates="posts"
    )
