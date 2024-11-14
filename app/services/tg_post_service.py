import re
from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy import desc, asc, func, select, between
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from ..db.models import TGPostModel


async def get_filtered_tg_posts(
    status: str | None,
    price: str | None,
    duration: str | None,
    is_new: bool | None,
    rooms: str | None,
    area: str | None,
    floor: str | None,
    pets_allowed: bool | None,
    sort_by: str | None,
    sort_order: bool | None,
    page_num: int | None,
    limit: int | None,
    db: AsyncSession,
) -> tuple[int, list[TGPostModel]]:
    query = select(TGPostModel)

    # status filter
    if status == "today":
        status = date.today()
    elif status is not None:
        status = date.fromisoformat(status)
    if status is not None:
        query = query.where(TGPostModel.status <= status)
    # price filter
    if price is not None and "-" in price:
        price_bottom, price_top = price.split("-")
        query = query.where(
            between(TGPostModel.price, int(price_bottom), int(price_top))
        )
    elif price is not None:
        query = query.where(TGPostModel.price <= int(price))
    # duration filter
    if duration is not None and "-" in duration:
        duration_bottom, duration_top = duration.split("-")
        query = query.where(
            between(TGPostModel.duration, int(duration_bottom), int(duration_top))
        )
    elif duration is not None:
        query = query.where(TGPostModel.duration <= int(duration))
    # rooms filter
    if rooms is not None and "-" in rooms:
        rooms_bottom, rooms_top = rooms.split("-")
        query = query.where(
            between(TGPostModel.rooms, int(rooms_bottom), int(rooms_top))
        )
    elif rooms is not None:
        query = query.between(TGPostModel.rooms, float(rooms), float(rooms) + 0.5)
    # area filter
    if area is not None and "-" in area:
        area_bottom, area_top = area.split("-")
        query = query.where(between(TGPostModel.area, int(area_bottom), int(area_top)))
    elif area is not None:
        query = query.where(between(TGPostModel.area, int(area) - 10, int(area) + 10))
    # floor filter
    if floor is not None and "-" in floor:
        floor_bottom, floor_top = floor.split("-")
        query = query.where(
            between(TGPostModel.floor, int(floor_bottom), int(floor_top))
        )
    elif floor is not None:
        query = query.where(TGPostModel.floor == int(floor))
    # is_new filter
    if is_new is not None:
        query = query.where(TGPostModel.is_new == is_new)
    # pets_allowed filter
    if pets_allowed is not None:
        query = query.where(TGPostModel.pets_allowed == pets_allowed)
    # sort_order filter
    if sort_order is None:
        sort_order = False
    # sort_by filter
    if sort_by is not None:
        sort_by = getattr(TGPostModel, sort_by, None)
    if sort_by is None:
        sort_by = getattr(TGPostModel, "publication_datetime", None)

    query = query.order_by(asc(sort_by) if sort_order else desc(sort_by))

    # get total count of posts
    count_query = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_query.scalar()
    # get items
    query = query.offset((page_num - 1) * limit).limit(limit)
    posts_query = await db.execute(query)
    posts = posts_query.scalars().all()

    return (total, posts)
