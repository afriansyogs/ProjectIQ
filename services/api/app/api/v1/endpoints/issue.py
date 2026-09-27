import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import (
    get_current_user,
    get_db_session,
    verify_issue_access,
    verify_project_access,
)
from app.infrastructure.db.models.user import User
from app.infrastructure.db.models.work_management import (
    ActivityType,
    Issue,
    IssueActivity,
    IssuePriority,
    IssueStatus,
    IssueType,
)
from app.schemas.issue import (
    IssueActivityResponse,
    IssueCreateRequest,
    IssueResponse,
    IssueUpdateRequest,
)

router = APIRouter()


@router.post(
    "/projects/{project_id}/issues",
    response_model=IssueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new issue inside a project",
)
async def create_issue(
    project_id: uuid.UUID,
    data: IssueCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> IssueResponse:
    project = await verify_project_access(db, project_id, current_user.id)

    seq_query = select(func.coalesce(func.max(Issue.sequence_id), 0) + 1).where(
        Issue.project_id == project_id
    )
    next_sequence_id = (await db.execute(seq_query)).scalar_one()

    completed_at = (
        datetime.now(timezone.utc) if data.status == IssueStatus.DONE else None
    )

    new_issue = Issue(
        project_id=project_id,
        sequence_id=next_sequence_id,
        title=data.title,
        description=data.description,
        issue_type=data.issue_type,
        status=data.status,
        priority=data.priority,
        story_points=data.story_points,
        assignee_id=data.assignee_id,
        module_id=data.module_id,
        cycle_id=data.cycle_id,
        reporter_id=current_user.id,
        completed_at=completed_at,
    )
    db.add(new_issue)
    await db.flush()

    activity = IssueActivity(
        issue_id=new_issue.id,
        actor_id=current_user.id,
        activity_type=ActivityType.CREATED,
        new_value=new_issue.title,
    )
    db.add(activity)

    await db.commit()
    await db.refresh(new_issue)

    response = IssueResponse.model_validate(new_issue)
    response.issue_key = f"{project.identifier}-{new_issue.sequence_id}"
    return response


@router.get(
    "/projects/{project_id}/issues",
    response_model=List[IssueResponse],
    status_code=status.HTTP_200_OK,
    summary="List all issues in a project with optional Kanban filtering",
)
async def list_project_issues(
    project_id: uuid.UUID,
    issue_status: Optional[IssueStatus] = Query(None, alias="status"),
    priority: Optional[IssuePriority] = Query(None),
    assignee_id: Optional[uuid.UUID] = Query(None),
    issue_type: Optional[IssueType] = Query(None),
    cycle_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> List[IssueResponse]:
    project = await verify_project_access(db, project_id, current_user.id)

    query = select(Issue).where(Issue.project_id == project_id)

    if issue_status:
        query = query.where(Issue.status == issue_status)
    if priority:
        query = query.where(Issue.priority == priority)
    if assignee_id:
        query = query.where(Issue.assignee_id == assignee_id)
    if issue_type:
        query = query.where(Issue.issue_type == issue_type)
    if cycle_id:
        query = query.where(Issue.cycle_id == cycle_id)

    query = query.order_by(Issue.sequence_id.asc())
    results = (await db.execute(query)).scalars().all()

    response_items = []
    for issue in results:
        item = IssueResponse.model_validate(issue)
        item.issue_key = f"{project.identifier}-{issue.sequence_id}"
        response_items.append(item)

    return response_items


@router.get(
    "/issues/{issue_id}",
    response_model=IssueResponse,
    status_code=status.HTTP_200_OK,
    summary="Get details of a specific issue",
)
async def get_issue(
    issue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> IssueResponse:
    issue, project = await verify_issue_access(db, issue_id, current_user.id)
    response = IssueResponse.model_validate(issue)
    response.issue_key = f"{project.identifier}-{issue.sequence_id}"
    return response


@router.patch(
    "/issues/{issue_id}",
    response_model=IssueResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an issue and record audit activity changes",
)
async def update_issue(
    issue_id: uuid.UUID,
    data: IssueUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> IssueResponse:
    issue, project = await verify_issue_access(db, issue_id, current_user.id)

    if data.status is not None and data.status != issue.status:
        activity = IssueActivity(
            issue_id=issue.id,
            actor_id=current_user.id,
            activity_type=ActivityType.STATUS_CHANGE,
            old_value=issue.status.value,
            new_value=data.status.value,
        )
        db.add(activity)

        if data.status == IssueStatus.DONE:
            issue.completed_at = datetime.now(timezone.utc)
        elif issue.status == IssueStatus.DONE:
            issue.completed_at = None

        issue.status = data.status

    if data.assignee_id is not None and data.assignee_id != issue.assignee_id:
        activity = IssueActivity(
            issue_id=issue.id,
            actor_id=current_user.id,
            activity_type=ActivityType.ASSIGNEE_CHANGE,
            old_value=str(issue.assignee_id) if issue.assignee_id else None,
            new_value=str(data.assignee_id),
        )
        db.add(activity)
        issue.assignee_id = data.assignee_id

    if data.story_points is not None and data.story_points != issue.story_points:
        activity = IssueActivity(
            issue_id=issue.id,
            actor_id=current_user.id,
            activity_type=ActivityType.ESTIMATE_CHANGE,
            old_value=str(issue.story_points) if issue.story_points is not None else None,
            new_value=str(data.story_points),
        )
        db.add(activity)
        issue.story_points = data.story_points

    if data.title is not None:
        issue.title = data.title
    if data.description is not None:
        issue.description = data.description
    if data.issue_type is not None:
        issue.issue_type = data.issue_type
    if data.priority is not None:
        issue.priority = data.priority
    if data.module_id is not None:
        issue.module_id = data.module_id
    if data.cycle_id is not None:
        issue.cycle_id = data.cycle_id

    await db.commit()
    await db.refresh(issue)

    response = IssueResponse.model_validate(issue)
    response.issue_key = f"{project.identifier}-{issue.sequence_id}"
    return response


@router.get(
    "/issues/{issue_id}/activities",
    response_model=List[IssueActivityResponse],
    status_code=status.HTTP_200_OK,
    summary="Get chronological audit activity log for an issue",
)
async def list_issue_activities(
    issue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> List[IssueActivityResponse]:
    issue, _ = await verify_issue_access(db, issue_id, current_user.id)

    query = (
        select(IssueActivity)
        .where(IssueActivity.issue_id == issue_id)
        .order_by(IssueActivity.created_at.desc())
    )
    activities = (await db.execute(query)).scalars().all()
    return list(activities)