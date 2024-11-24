from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import oauth2_scheme, verify_access_token
from ..db.connection import get_db
from ..schemas import PostResponse, PostCreate, PostUpdate
from ..services.post_service import (
    get_posts_list,
    get_post,
    create_post_logic,
    update_post_logic,
)

router = APIRouter()


# TODO:


@router.post("/")
async def create_post(
    request: Request,
    post_schema: PostCreate = Depends(),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not token:
        token = request.cookies.get("access_token")

    username = verify_access_token(token=token)
    post, large_files = await create_post_logic(
        post_schema=post_schema, username=username, db=db
    )

    response = {
        "post": PostResponse.model_validate(post, from_attributes=True),
        "large_files": large_files,
    }

    return response


@router.get("/my_posts")
async def posts_list(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not token:
        token = request.cookies.get("access_token")

    username = verify_access_token(token=token)

    posts_model = await get_posts_list(db=db, username=username)
    posts = [
        PostResponse.model_validate(post_model, from_attributes=True)
        for post_model in posts_model
    ]

    return {"posts": posts, "total": len(posts)}


@router.get("/{post_id}")
async def show_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await get_post(post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return PostResponse.model_validate(post, from_attributes=True)


@router.put("/{post_id}")
async def update_post(
    request: Request,
    post_id: int,
    update_data: PostUpdate = Depends(),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not token:
        token = request.cookies.get("access_token")

    username = verify_access_token(token=token)

    post, large_images = await update_post_logic(
        post_id=post_id, username=username, update_data=update_data, db=db
    )

    return {
        "post": PostResponse.model_validate(post, from_attributes=True),
        "large_images": large_images,
    }


# @router.delete("/{post_id}")
# async def delete_post(db: AsyncSession = Depends(get_db)):
#     return {"message": "Post deleted successfully"}
