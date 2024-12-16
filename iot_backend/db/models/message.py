from datetime import datetime
from uuid import uuid4
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship

from iot_backend.db.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    channel_id = Column(String, nullable=False)
    publisher = Column(String, nullable=False)
    protocol = Column(String(100), nullable=True, default="http")
    subtopic = Column(String(100), nullable=True)
    base_name = Column(String(100), nullable=False)
    base_unit = Column(String(100), nullable=False)
    base_value = Column(Float, nullable=False)
    base_time = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    unit = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    time = Column(Integer, nullable=False)
    string_value = Column(String(255), nullable=True)
    bool_value = Column(Boolean, nullable=True)
    data_value = Column(String(255), nullable=True)
    sum_value = Column(Float, nullable=True)

    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=True)
    user_id = Column(UUID, ForeignKey("user.id"), nullable=True)

    device = relationship("Device", back_populates="messages")
    tag = relationship("Tag", back_populates="messages")
    user = relationship("User", back_populates="messages")
