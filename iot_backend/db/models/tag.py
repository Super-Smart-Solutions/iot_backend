from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from iot_backend.db.base import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, unique=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    name = Column(String, nullable=False)
    label = Column(String, nullable=False)
    target = Column(Integer, nullable=True)
    unit = Column(String, nullable=True)
    multiplier = Column(Float, nullable=True)
    mask = Column(JSON, nullable=True)
    graphed = Column(Boolean, default=False)

    user_id = Column(UUID, ForeignKey("user.id"), nullable=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self) -> str:
        return self.name
