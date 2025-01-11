import os
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.utils import save_image
from db.models import PostModel, CategoryModel
from schemas import PostCreate, PostUpdate
from services.user_service import get_user
from routes.category_route import get_parent_categories, get_subcategories

IMAGES_DIR = "./app/content/post_images"
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5mb in bytes


def download_post_images(images: list[UploadFile], dir: str) -> tuple[str, str]:
    # Downloading images to the server
    images_paths = []
    large_images = []
    for image in images:
        if image.size > MAX_IMAGE_SIZE:
            large_images.append(image.filename)
        else:
            images_paths.append(save_image(image=image, dir=dir))

    return images_paths, large_images


async def create_post_logic(
    post_schema: PostCreate, username: str, db: AsyncSession
) -> tuple[PostModel, list[str] | None]:
    user = await get_user(username=username, db=db)

    query = select(func.max(PostModel.id))
    result = await db.execute(query)
    last_post_id = result.scalar()
    if not last_post_id:
        next_post_id = 1
    else:
        next_post_id = last_post_id + 1

    post_dir = os.path.join(IMAGES_DIR, f"user{str(user.id)}", f"post{next_post_id}")
    if not os.path.exists(post_dir):
        os.makedirs(post_dir, exist_ok=True)

    images_paths, large_images = download_post_images(post_schema.images, dir=post_dir)

    # Checking if the category exists
    if post_schema.category_id not in [
        available_categories.id
        for available_categories in await get_parent_categories(db=db)
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found"
        )

    # Checking if the subcategory exists
    if post_schema.subcategory_id:
        if post_schema.subcategory_id not in [
            available_subcategories.id
            for available_subcategories in await get_subcategories(
                parent_id=post_schema.category_id, db=db
            )
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Subcategory not found"
            )

    post_schema.images = images_paths
    post = PostModel(**post_schema.model_dump(), author_id=user.id)

    db.add(post)
    await db.commit()
    await db.refresh(post)

    return post, large_images


async def get_posts_list(username: str, db: AsyncSession) -> list[PostModel] | None:
    user = await get_user(username=username, db=db)

    query = select(PostModel).filter(PostModel.author_id == user.id)
    result = await db.execute(query)
    posts = result.scalars().all()

    return posts


async def get_post(post_id: int, db: AsyncSession) -> PostModel | None:
    query = select(PostModel).filter(PostModel.id == post_id)

    result = await db.execute(query)
    post = result.scalar()

    return post


async def update_post_logic(
    post_id: int, username: str, update_data: PostUpdate, db: AsyncSession
) -> tuple[PostModel, list[str] | None]:
    user = await get_user(username=username, db=db)

    query = select(PostModel).filter(PostModel.id == post_id)
    result = await db.execute(query)
    post = result.scalar()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if user.id != post.author_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Updating post images if they were changed

    large_images = []
    images_paths = []
    if update_data.images:
        images_paths, large_images = download_post_images(
            update_data.images,
            dir=os.path.join(IMAGES_DIR, f"user{str(user.id)}", f"post{post_id}"),
        )

    # Deleting images from the server if they were deleted in update data
    if update_data.images_indexes_to_delete:
        for image in update_data.images_indexes_to_delete:
            os.remove(post.images[image])
            del post.images[image]

    update_data.images = post.images + images_paths

    # Updating post data
    for key, value in update_data.model_dump(
        exclude_unset=True, exclude_none=True
    ).items():
        setattr(post, key, value)

    await db.commit()
    await db.refresh(post)

    return post, large_images
