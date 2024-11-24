from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .. import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    parent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )

    parent = relationship("CategoryModel", remote_side=[id], backref="subcategories")

    posts = relationship(
        "PostModel",
        back_populates="category",
        foreign_keys="PostModel.category_id",
    )

    subcategory_posts = relationship(
        "PostModel",
        back_populates="subcategory",
        foreign_keys="PostModel.subcategory_id",
    )
