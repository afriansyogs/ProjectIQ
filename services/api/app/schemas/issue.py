import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.infrastructure.db.models.work_management import (
    ActivityType,
    IssuePriority,
    IssueStatus,
    IssueType,
)


class IssueCreateRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Concise summary title of the issue",
        examples=["Implement OAuth2 authentication flow"],
    )
    description: Optional[str] = Field(
        None,
        max_length=10000,
        description="Detailed description or markdown specification of the task",
        examples=["Use PKCE with authorization code flow for web and mobile clients."],
    )
    issue_type: IssueType = Field(
        default=IssueType.TASK,
        description="Category classification of the issue (TASK, BUG, FEATURE, IMPROVEMENT)",
    )
    status: IssueStatus = Field(
        default=IssueStatus.TODO,
        description="Initial workflow column status",
    )
    priority: IssuePriority = Field(
        default=IssuePriority.NONE,
        description="Urgency priority level (URGENT, HIGH, MEDIUM, LOW, NONE)",
    )
    story_points: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Estimated effort complexity story points (Fibonacci scale e.g. 1, 2, 3, 5, 8)",
    )
    assignee_id: Optional[uuid.UUID] = Field(
        None,
        description="Optional UUID of the user assigned to work on this issue",
    )
    module_id: Optional[uuid.UUID] = Field(
        None,
        description="Optional epic / feature module UUID this issue belongs to",
    )
    cycle_id: Optional[uuid.UUID] = Field(
        None,
        description="Optional sprint cycle UUID this issue is planned into",
    )


class IssueUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=10000)
    issue_type: Optional[IssueType] = None
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    story_points: Optional[int] = Field(None, ge=0, le=100)
    assignee_id: Optional[uuid.UUID] = None
    module_id: Optional[uuid.UUID] = None
    cycle_id: Optional[uuid.UUID] = None


class IssueResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique issue UUID")
    project_id: uuid.UUID = Field(..., description="Parent project UUID")
    sequence_id: int = Field(..., description="Project-scoped sequential issue number")
    issue_key: Optional[str] = Field(
        None,
        description="Formatted ticket identifier (e.g. 'MOB-12')",
    )
    title: str = Field(..., description="Issue title")
    description: Optional[str] = Field(None, description="Issue description")
    issue_type: IssueType = Field(..., description="Issue category")
    status: IssueStatus = Field(..., description="Current workflow state")
    priority: IssuePriority = Field(..., description="Priority level")
    story_points: Optional[int] = Field(None, description="Story point estimate")
    assignee_id: Optional[uuid.UUID] = Field(None, description="Assignee user UUID")
    reporter_id: uuid.UUID = Field(..., description="Reporter user UUID")
    completed_at: Optional[datetime] = Field(None, description="Timestamp when moved to DONE")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")

    model_config = ConfigDict(from_attributes=True)


class IssueActivityResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique activity log UUID")
    issue_id: uuid.UUID = Field(..., description="Target issue UUID")
    actor_id: Optional[uuid.UUID] = Field(None, description="UUID of user who performed the change")
    activity_type: ActivityType = Field(..., description="Action type performed")
    old_value: Optional[str] = Field(None, description="Previous state or value")
    new_value: Optional[str] = Field(None, description="Updated state or value")
    comment: Optional[str] = Field(None, description="Optional textual comment")
    created_at: datetime = Field(..., description="Timestamp of the action")

    model_config = ConfigDict(from_attributes=True)
