from datetime import datetime
from fastapi import UploadFile
from pydantic import BaseModel, Field, field_validator, root_validator
from typing import Optional


class PostResponse(BaseModel):
    id: int
    location: str
    title: str
    price: Optional[float] = None
    description: Optional[str] = None
    is_new: Optional[bool] = None
    images: list[str]
    publication_datetime: datetime
    author_id: int
    category_id: int
    subcategory_id: Optional[int] = None


class PostCreate(BaseModel):
    location: str
    title: str
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None)
    is_new: Optional[bool] = Field(None)
    category_id: int
    subcategory_id: Optional[int] = Field(None)
    images: Optional[list[UploadFile]] = Field(default=[])


class PostUpdate(BaseModel):
    location: Optional[str] = Field(None)
    title: Optional[str] = Field(None)
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None)
    is_new: Optional[bool] = Field(None)
    images: Optional[list[UploadFile]] = Field([])
    images_indexes_to_delete: Optional[list[int]] = Field([])

    # FIXME:
    @root_validator(pre=True)
    def split_index_string(cls, values):
        if "images_index_to_delete" in values and values["images_index_to_delete"]:
            values["images_index_to_delete"] = list(
                map(int, values["images_index_to_delete"].split(","))
            )
        return values
