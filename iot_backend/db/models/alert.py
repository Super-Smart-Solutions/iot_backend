from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from iot_backend.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    comparator = Column(String, nullable=False)
    threshold = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    # channel_id = Column(String, nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"))
    user_id = Column(UUID, ForeignKey("user.id"))

    check_external_id = Column(String, nullable=False)
    check_external_message_template = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    notifications = relationship("Notification", backref="alert")

    def __str__(self) -> str:
        return self.name
