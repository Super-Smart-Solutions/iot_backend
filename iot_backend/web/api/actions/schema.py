from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ActionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ActionBase(BaseModel):
    device_id: int
    is_enabled: bool
    values: List[str]


class ActionCreate(ActionBase):
    pass


class ActionUpdate(BaseModel):
    is_enabled: Optional[bool]
    values: Optional[List[str]]


class ActionRead(ActionBase):
    id: int
    status: ActionStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
