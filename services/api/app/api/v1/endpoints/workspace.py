import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import (
    get_current_user,
    get_db_session,
    get_user_by_email_or_username,
    verify_workspace_membership,
)
from app.core.utils import slugify
from app.infrastructure.db.models.user import User
from app.infrastructure.db.models.workspace import Workspace, WorkspaceMember, WorkspaceMemberRole
from app.schemas.workspace import (
    WorkspaceCreateRequest,
    WorkspaceMemberAddRequest,
    WorkspaceMemberResponse,
    WorkspaceResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workspace",
)
async def create_workspace(
    data: WorkspaceCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Workspace:
    slug = data.slug or slugify(data.name)
    if not slug:
        slug = f"ws-{uuid.uuid4().hex[:8]}"

    slug_check = select(Workspace).where(Workspace.slug == slug)
    existing_ws = (await db.execute(slug_check)).scalar_one_or_none()
    if existing_ws:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workspace slug '{slug}' is already taken. Please choose another.",
        )

    workspace = Workspace(
        name=data.name,
        slug=slug,
        description=data.description,
        owner_id=current_user.id,
    )
    db.add(workspace)
    await db.flush()

    admin_member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role=WorkspaceMemberRole.ADMIN,
    )
    db.add(admin_member)

    await db.commit()
    await db.refresh(workspace)
    return workspace


@router.get(
    "",
    response_model=List[WorkspaceResponse],
    status_code=status.HTTP_200_OK,
    summary="List all workspaces the authenticated user belongs to",
)
async def list_user_workspaces(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> List[Workspace]:
    query = (
        select(Workspace)
        .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
        .where(WorkspaceMember.user_id == current_user.id)
        .order_by(Workspace.created_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get details of a specific workspace",
)
async def get_workspace(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Workspace:
    await verify_workspace_membership(db, workspace_id, current_user.id)

    workspace = (
        await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    ).scalar_one_or_none()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )
    return workspace


@router.get(
    "/{workspace_id}/members",
    response_model=List[WorkspaceMemberResponse],
    status_code=status.HTTP_200_OK,
    summary="List all members in a workspace",
)
async def list_workspace_members(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> List[WorkspaceMemberResponse]:
    await verify_workspace_membership(db, workspace_id, current_user.id)

    query = (
        select(WorkspaceMember, User)
        .join(User, WorkspaceMember.user_id == User.id)
        .where(WorkspaceMember.workspace_id == workspace_id)
        .order_by(WorkspaceMember.created_at.asc())
    )
    results = (await db.execute(query)).all()

    return [
        WorkspaceMemberResponse(
            id=member.id,
            workspace_id=member.workspace_id,
            user_id=member.user_id,
            role=member.role,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            created_at=member.created_at,
        )
        for member, user in results
    ]


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite/add a member to a workspace (Admin only)",
)
async def add_workspace_member(
    workspace_id: uuid.UUID,
    data: WorkspaceMemberAddRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> WorkspaceMemberResponse:
    await verify_workspace_membership(
        db, workspace_id, current_user.id, required_roles=[WorkspaceMemberRole.ADMIN]
    )

    target_user = await get_user_by_email_or_username(db, data.email_or_username)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{data.email_or_username}' not found.",
        )

    existing_membership = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == target_user.id,
    )
    already_member = (await db.execute(existing_membership)).scalar_one_or_none()
    if already_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this workspace.",
        )

    new_member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=target_user.id,
        role=data.role,
    )
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)

    return WorkspaceMemberResponse(
        id=new_member.id,
        workspace_id=new_member.workspace_id,
        user_id=new_member.user_id,
        role=new_member.role,
        email=target_user.email,
        username=target_user.username,
        full_name=target_user.full_name,
        created_at=new_member.created_at,
    )
