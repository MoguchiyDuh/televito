from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    UploadFile,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import verify_access_token, oauth2_scheme
from ..schemas.user_schema import (
    UserCreate,
    UserDelete,
    UserUpdate,
    UserInfo,
    UserChangePassword,
)
from ..db.connection import get_db
from ..services.user_service import (
    delete_user_logic,
    get_user,
    create_user_logic,
    update_user_logic,
    authenticate_user,
    change_user_password_logic,
)

router = APIRouter()


@router.post("/register", response_model=UserInfo)
async def register(user_schema: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user_logic(user_schema=user_schema, db=db)


@router.post("/token")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    print(form_data)
    access_token = await authenticate_user(
        db=db, credentials=form_data.username, password=form_data.password
    )
    response.set_cookie(
        key="access_token", value=access_token, httponly=True, max_age=3600
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=UserInfo)
async def read_profile(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not token:
        access_token = request.cookies.get("access_token")
        username = await verify_access_token(token=access_token)

    user = await get_user(username=username, db=db)

    return UserInfo.model_validate(user, from_attributes=True)


@router.put("/profile", response_model=UserInfo)
async def update_profile(
    request: Request,
    user_update: UserUpdate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    profile_photo: Optional[UploadFile] = None,
):
    if not username:
        access_token = request.cookies.get("access_token")
        username = await verify_access_token(token=access_token)

    user = await update_user_logic(
        username=username, update_data=user_update, db=db, profile_photo=profile_photo
    )
    return UserInfo.model_validate(user, from_attributes=True)


@router.put("/change-password", response_model=UserInfo)
async def change_user_password(
    request: Request,
    password_schema: UserChangePassword,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):

    if not username:
        access_token = request.cookies.get("access_token")
        username = await verify_access_token(token=access_token)

    user = await change_user_password_logic(
        username=username, password_schema=password_schema, db=db
    )
    return UserInfo.model_validate(user, from_attributes=True)


@router.delete("/profile")
async def delete_profile(
    request: Request,
    password_schema: UserDelete,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not username:
        access_token = request.cookies.get("access_token")
        username = await verify_access_token(token=access_token)

    return await delete_user_logic(
        username=username, password=password_schema.password, db=db
    )
