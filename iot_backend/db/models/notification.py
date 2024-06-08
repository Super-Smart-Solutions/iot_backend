from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from iot_backend.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    message = Column(String, nullable=False)
    level = Column(String, nullable=False)
    check_id = Column(String, nullable=False)
    notification_endpoint_id = Column(String, nullable=False)
    notification_rule_id = Column(String, nullable=False)

    alert_id = Column(Integer, ForeignKey("alerts.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))
    user_id = Column(UUID, ForeignKey("user.id"))

    def __str__(self) -> str:
        return f"{self.level} {self.message}"
