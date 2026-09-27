import uuid
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select

from app.core.config import settings
from app.core.database import get_async_db
from app.core.security import decode_access_token
from app.infrastructure.db.models.project import Project
from app.infrastructure.db.models.user import User, UserRole
from app.infrastructure.db.models.workspace import WorkspaceMember, WorkspaceMemberRole

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional asynchronous database session dependency."""
    async for session in get_async_db():
        yield session


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    header_token: Optional[str] = Depends(reusable_oauth2),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.cookies.get("access_token") or header_token
    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str: str = payload.get("sub")
    if not user_id_str:
        raise credentials_exception

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    query = select(User).where(User.id == user_uuid)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account.",
        )

    return user


async def verify_workspace_membership(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    required_roles: Optional[list[WorkspaceMemberRole]] = None,
) -> WorkspaceMember:
    query = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id,
    )
    membership = (await db.execute(query)).scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace.",
        )

    if required_roles and membership.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Action requires one of the following workspace roles: {[r.value for r in required_roles]}.",
        )

    return membership


async def get_user_by_email_or_username(
    db: AsyncSession,
    identifier: str,
) -> Optional[User]:
    clean_identifier = identifier.strip()
    query = select(User).where(
        or_(
            User.email == clean_identifier,
            User.username == clean_identifier,
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


def require_system_role(*allowed_roles: UserRole):
    #RBAC
    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action requires one of the following system roles: {[r.value for r in allowed_roles]}.",
            )
        return current_user

    return role_checker


async def verify_project_access(
    db: AsyncSession,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    required_workspace_roles: Optional[list[WorkspaceMemberRole]] = None,
) -> Project:
    query = select(Project).where(Project.id == project_id)
    project = (await db.execute(query)).scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    await verify_workspace_membership(
        db=db,
        workspace_id=project.workspace_id,
        user_id=user_id,
        required_roles=required_workspace_roles,
    )

    return project


