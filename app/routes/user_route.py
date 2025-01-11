from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import oauth2_scheme, verify_access_token
from db.connection import get_db
from schemas.user_schema import (
    UserChangePassword,
    UserCreate,
    UserDelete,
    UserProfileResponse,
    UserUpdate,
)
from services.user_service import (
    authenticate_user,
    change_user_password_logic,
    create_user_logic,
    delete_user_logic,
    get_user,
    update_user_logic,
)


router = APIRouter()


@router.post("/register")
async def register(
    user_schema: UserCreate = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await create_user_logic(user_schema=user_schema, db=db)

    return {
        "message": "User created successfully",
        "user": UserProfileResponse.model_validate(user, from_attributes=True),
    }


@router.post("/token")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    access_token = await authenticate_user(
        db=db, credentials=form_data.username, password=form_data.password
    )
    # max age is 30 minutes
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=30 * 60,
        secure=True,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def show_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user(user_id=user_id, db=db)

    return UserProfileResponse.model_validate(user, from_attributes=True)


@router.get("/profile")
async def my_profile(
    request: Request,
    token=Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not token:
        token = request.cookies.get("access_token")

    username = verify_access_token(token=token)

    user = await get_user(username=username, db=db)

    return UserProfileResponse.model_validate(user, from_attributes=True)


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    request: Request,
    user_update: UserUpdate = Depends(),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not token:
        token = request.cookies.get("access_token")

    username = verify_access_token(token=token)

    user = await update_user_logic(username=username, update_data=user_update, db=db)

    return UserProfileResponse.model_validate(user, from_attributes=True)


@router.put("/change-password", response_model=UserProfileResponse)
async def change_user_password(
    request: Request,
    password_schema: UserChangePassword = Depends(),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not token:
        token = request.cookies.get("access_token")

    username = verify_access_token(token=token)

    user = await change_user_password_logic(
        username=username, password_schema=password_schema, db=db
    )

    return UserProfileResponse.model_validate(user, from_attributes=True)


@router.delete("/profile")
async def delete_my_profile(
    request: Request,
    password_schema: UserDelete = Depends(),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not token:
        token = request.cookies.get("access_token")

    username = verify_access_token(token=token)
    deletion_response = await delete_user_logic(
        username=username, password=password_schema.password, db=db
    )
    request.cookies.clear()

    return deletion_response
