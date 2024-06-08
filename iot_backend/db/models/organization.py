import datetime

from sqlalchemy import BigInteger, Column, DateTime, Unicode
from sqlalchemy.orm import relationship

from iot_backend.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Unicode(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    users = relationship("User", backref="organization")

    devices = relationship("Device", backref="organization")

    def __str__(self) -> str:
        return self.name
