from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):

    name: str
    label: str
    target: int
    unit: str
    multiplier: float
    mask: dict
    graphed: bool
    device_id: Optional[int] = None


class TagInputDTO(TagBase):
    pass


class TagDTO(TagBase):
    id: int
    uuid: UUID
    device_id: Optional[int] = None
    user_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
