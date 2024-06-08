import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Unicode
from sqlalchemy.orm import relationship

from iot_backend.db.base import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Unicode(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    organization_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=True)
    users = relationship("User", backref="group")

    def __str__(self) -> str:
        return self.name
