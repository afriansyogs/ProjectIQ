from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import (
    get_current_user,
    get_db_session,
    get_user_by_email_or_username,
)
from app.core.security import create_access_token, get_password_hash, verify_password
from app.infrastructure.db.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserSignupRequest,
    UserResponse,
)

router = APIRouter()

COOKIE_NAME = "access_token"
IS_PRODUCTION = settings.ENVIRONMENT.lower() == "production"


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign up a new account",
)
async def signup(
    data: UserSignupRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
) -> User:
    email_check = select(User).where(User.email == data.email)
    existing_email = (await db.execute(email_check)).scalar_one_or_none()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    username_check = select(User).where(User.username == data.username)
    existing_username = (await db.execute(username_check)).scalar_one_or_none()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken. Please choose another.",
        )

    hashed_password = get_password_hash(data.password)
    new_user = User(
        email=data.email,
        username=data.username,
        password=hashed_password,
        full_name=data.full_name,
        role=data.role,
        is_active=True,
        is_verified=False,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token(subject=new_user.id)
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue JWT access token",
)
async def login(
    data: UserLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username/email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await get_user_by_email_or_username(db, data.username_or_email)
    if not user:
        raise credentials_exception

    if not verify_password(data.password, user.password):
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is currently inactive. Contact your administrator.",
        )

    access_token = create_access_token(subject=user.id)
    expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="lax",
        max_age=expires_in_seconds,
        path="/",
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in_seconds,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Log out user and clear authentication session cookie",
)
async def logout(
    response: Response,
) -> dict:
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
    )
    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
    