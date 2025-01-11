from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from db.connection import get_db
from db.models import CategoryModel

router = APIRouter()


@router.get("/")
async def get_parent_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CategoryModel).filter(CategoryModel.parent_id == None)
    )
    categories = result.scalars().all()

    return categories


@router.get("/{parent_id}/subcategories")
async def get_subcategories(parent_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CategoryModel).filter(CategoryModel.parent_id == parent_id)
    )
    subcategories = result.scalars().all()

    return subcategories
