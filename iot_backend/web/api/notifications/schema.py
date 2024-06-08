from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
    message: str
    level: str
    check_id: str
    notification_endpoint_id: str
    notification_rule_id: str


class NotificationInputDTO(NotificationBase):
    """
    DTO for Notifications.

    It returned when accessing Notifications from the API.
    """

    pass


class NotificationDTO(NotificationBase):
    """DTO for creating new Notification."""

    id: int
    uuid: UUID
    alert_id: int
    device_id: int
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
