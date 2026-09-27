import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProjectCreateRequest(BaseModel):
    workspace_id: uuid.UUID = Field(
        ...,
        description="UUID of the parent workspace this project belongs to",
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Name of the project",
        examples=["Mobile Banking App"],
    )
    identifier: str = Field(
        ...,
        min_length=2,
        max_length=10,
        pattern=r"^[A-Z0-9]+$",
        description="Uppercase issue prefix key (e.g., 'MOB' generates 'MOB-1', 'MOB-2')",
        examples=["MOB"],
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional description of the project scope",
    )
    lead_id: Optional[uuid.UUID] = Field(
        None,
        description="Optional user UUID designated as Project Lead",
    )


class ProjectResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique project UUID")
    workspace_id: uuid.UUID = Field(..., description="Parent workspace UUID")
    name: str = Field(..., description="Project name")
    identifier: str = Field(..., description="Issue prefix identifier")
    description: Optional[str] = Field(None, description="Project scope description")
    lead_id: Optional[uuid.UUID] = Field(None, description="Project Lead user UUID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)