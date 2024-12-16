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
from sqlalchemy.orm import relationship

from iot_backend.db.base import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, unique=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    mainflux_channel_uuid = Column(UUID, nullable=True)
    name = Column(String, nullable=False, unique=True)
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

    messages = relationship("Message", back_populates="tag")

    def __str__(self) -> str:
        return self.name
