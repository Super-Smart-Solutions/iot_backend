from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DeviceType(str, Enum):
    node = "node"
    gateway = "gateway"


class DeviceBase(BaseModel):
    name: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = {}
    type: Optional[DeviceType] = None
    is_configured: Optional[bool] = False
    mainflux_thing_uuid: Optional[UUID] = None
    mainflux_thing_secret: Optional[UUID] = None
    parent_id: Optional[int] = None
    org_id: Optional[int] = None


class DeviceInputDTO(DeviceBase):
    pass


class DeviceDTO(BaseModel):
    id: int
    uuid: UUID
    name: str
    meta_data: dict = {}
    type: DeviceType
    is_configured: bool
    mainflux_thing_uuid: Optional[UUID] = None
    mainflux_thing_secret: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    parent_id: Optional[int] = None
    user_id: UUID
    org_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
