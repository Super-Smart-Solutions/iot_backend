from datetime import datetime
from pydantic import BaseModel


class OrganizationResponse(BaseModel): 
    """Represents an organization with an ID and name."""

    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class OrganizationCreate(BaseModel):
    """Represents the data required to create a new organization."""

    name: str
