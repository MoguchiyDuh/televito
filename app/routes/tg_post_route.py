from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..db.connection import get_db
from ..db.models import TGPostModel
from ..schemas import TGPostSchema, ShortTGPostSchema
from ..services.tg_post_service import get_filtered_tg_posts

router = APIRouter()


@router.get("/", name="tg_posts_list")
async def tg_posts_list(
    request: Request,
    status: str | None = Query(None, pattern=r"\d{4}-\d{1,2}-\d{1,2}|today"),
    price: str | None = Query(None, pattern=r"\d+|\d+-\d+"),
    duration: str | None = Query(None, pattern=r"\d+|\d+-\d+"),
    is_new: bool | None = Query(None),
    rooms: str | None = Query(None, pattern=r"\d+|\d+-\d+"),
    area: str | None = Query(None, pattern=r"\d+|\d+-\d+"),
    floor: str | None = Query(None, pattern=r"\d+|\d+-\d+"),
    pets_allowed: bool | None = Query(None),
    sort_by: Literal["status", "duration", "rooms", "area", "floor"] | None = Query(
        None
    ),
    sort_order: bool | None = Query(None),  # 0 - desc, 1 - asc
    page_num: int | None = Query(1, ge=1),
    limit: int | None = Query(20, ge=1),
    db: AsyncSession = Depends(get_db),
):
    total, items = await get_filtered_tg_posts(
        status=status,
        price=price,
        duration=duration,
        is_new=is_new,
        rooms=rooms,
        area=area,
        floor=floor,
        pets_allowed=pets_allowed,
        sort_by=sort_by,
        sort_order=sort_order,
        page_num=page_num,
        limit=limit,
        db=db,
    )

    response = {
        "items": [ShortTGPostSchema.from_orm_model(item) for item in items],
        "pagination": {"next": "", "prev": ""},
        "page": page_num,
        "limit": limit,
        "total": total,
    }

    # Check for the previous page link
    if page_num > 1:
        response["pagination"][
            "prev"
        ] = f"{request.url_for('tg_posts_list')}?page_num={page_num-1}&limit={limit}"

    # Check for the next page link
    if total >= limit * page_num:
        response["pagination"][
            "next"
        ] = f"{request.url_for('tg_posts_list')}?page_num={page_num+1}&limit={limit}"

    return response


# Get post details by ID
@router.get("/{post_id}", response_model=TGPostSchema)
async def get_tg_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await db.execute(select(TGPostModel).filter(TGPostModel.id == post_id))
    post = post.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
