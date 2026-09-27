import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import (
    get_current_user,
    get_db_session,
    verify_project_access,
    verify_workspace_membership,
)
from app.infrastructure.db.models.project import Project
from app.infrastructure.db.models.user import User
from app.schemas.project import ProjectCreateRequest, ProjectResponse

router = APIRouter()


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project within a workspace",
)
async def create_project(
    data: ProjectCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Project:
    await verify_workspace_membership(db, data.workspace_id, current_user.id)

    identifier_upper = data.identifier.upper().strip()
    identifier_check = select(Project).where(
        Project.workspace_id == data.workspace_id,
        Project.identifier == identifier_upper,
    )
    existing_project = (await db.execute(identifier_check)).scalar_one_or_none()
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with identifier key '{identifier_upper}' already exists in this workspace.",
        )

    project = Project(
        workspace_id=data.workspace_id,
        name=data.name,
        identifier=identifier_upper,
        description=data.description,
        lead_id=data.lead_id or current_user.id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return project


@router.get(
    "",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List all projects in a workspace",
)
async def list_workspace_projects(
    workspace_id: uuid.UUID = Query(..., description="UUID of the workspace to list projects for"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> List[Project]:
    await verify_workspace_membership(db, workspace_id, current_user.id)

    query = (
        select(Project)
        .where(Project.workspace_id == workspace_id)
        .order_by(Project.created_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get details of a specific project",
)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Project:
    return await verify_project_access(db, project_id, current_user.id)