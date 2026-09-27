import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.infrastructure.db.models.workspace import WorkspaceMemberRole


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Display name of the organization workspace",
        examples=["Acme Corp"],
    )
    slug: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Unique URL slug (lowercase alphanumeric and hyphens). Auto-generated if omitted.",
        examples=["acme-corp"],
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional brief overview of this workspace",
        examples=["Primary engineering workspace for Acme Corp products"],
    )


class WorkspaceResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique workspace UUID")
    name: str = Field(..., description="Workspace display name")
    slug: str = Field(..., description="Workspace URL slug identifier")
    description: Optional[str] = Field(None, description="Workspace description")
    owner_id: uuid.UUID = Field(..., description="UUID of the workspace creator")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class WorkspaceMemberAddRequest(BaseModel):
    email_or_username: str = Field(
        ...,
        min_length=3,
        description="Email address or username of the user to invite",
        examples=["developer@company.com", "dev_gorge"],
    )
    role: WorkspaceMemberRole = Field(
        default=WorkspaceMemberRole.MEMBER,
        description="Permission level within the workspace (ADMIN, MEMBER, GUEST)",
    )


class WorkspaceMemberResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique membership record UUID")
    workspace_id: uuid.UUID = Field(..., description="Target workspace UUID")
    user_id: uuid.UUID = Field(..., description="User UUID")
    role: WorkspaceMemberRole = Field(..., description="Assigned role in workspace")
    email: Optional[str] = Field(None, description="User email address")
    username: Optional[str] = Field(None, description="Username")
    full_name: Optional[str] = Field(None, description="User full display name")
    created_at: datetime = Field(..., description="Membership creation timestamp")

    model_config = ConfigDict(from_attributes=True)
