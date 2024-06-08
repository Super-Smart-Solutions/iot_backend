from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Comparator(str, Enum):
    GREATER_THAN = "Greater than"
    LESS_THAN = "Less than"
    RANGE = "Range"


class AlertBase(BaseModel):
    name: str
    threshold: float
    comparator: Comparator


class AlertInputDTO(AlertBase):
    """
    DTO for alerts.

    It returned when accessing alerts from the API.
    """

    pass


class AlertDTO(AlertBase):
    """DTO for creating new alert."""

    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    check_external_id: str
    check_external_message_template: str
    status: bool
    device_id: int
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
