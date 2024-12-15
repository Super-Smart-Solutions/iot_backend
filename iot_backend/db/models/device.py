from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from iot_backend.db.base import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    name = Column(String(100))
    meta_data = Column(
        JSON, nullable=True, default={"longitude": None, "latitude": None}
    )
    type = Column(Enum("node", "gateway", name="device__type"))
    is_configured = Column(Boolean, default=False)
    mainflux_thing_uuid = Column(UUID, nullable=True)
    mainflux_thing_secret = Column(UUID, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent_id = Column(
        Integer, ForeignKey("devices.id"), nullable=True
    )  # One-to-One Relationship
    user_id = Column(UUID, ForeignKey("user.id"), nullable=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    parent = relationship("Device", remote_side=[id])

    # one-to-many relationship between Device and Alerts
    alerts = relationship("Alert", backref="device")

    # one-to-many relationship between Device and Notification
    notifications = relationship("Notification", backref="device")

    # one-to-many relationship between Device and Tag
    tags = relationship("Tag", backref="device")
    
    messages = relationship("Message", back_populates="device")

    actions = relationship("Action", back_populates="device")


    def configure(self):
        pass

    #     client = MainfluxClient()  # Initialize your Mainflux client
    #     thing = client.get_thing(external_node_id=self.uuid)  # Get the thing from Mainflux using the device's UUID
    #     self.is_configured = True
    #     self.mainflux_thing_uuid = thing.uuid  # Set the mainflux_thing_uuid to the thing's UUID
    #     self.secret = thing.credentials.secret

    def __str__(self) -> str:
        return self.name
