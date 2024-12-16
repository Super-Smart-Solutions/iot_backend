# type: ignore
import uuid
from typing import Optional

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from iot_backend.db.base import Base
from iot_backend.db.dependencies import get_db_session
from iot_backend.settings import settings


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Represents a user entity."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=True)
    group_id = Column(BigInteger, ForeignKey("groups.id"), nullable=True)

    # one-to-many relationship between User and Device
    devices = relationship("Device", backref="user")

    # one-to-many relationship between User and Alert
    alerts = relationship("Alert", backref="user")

    # one-to-many relationship between User and Notification
    notifications = relationship("Notification", backref="user")

    # one-to-many relationship between User and Tag
    tags = relationship("Tag", backref="user")

    messages = relationship("Message", back_populates="user")

    def __str__(self) -> str:
        return self.email


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Represents a read command for a user."""

    organization_id: Optional[int] = None
    group_id: Optional[int] = None


class UserCreate(schemas.BaseUserCreate):
    """Represents a create command for a user."""

    organization_id: int = None
    group_id: int = None


class UserUpdate(schemas.BaseUserUpdate):
    """Represents an update command for a user."""

    organization_id: int = None
    group_id: int = None


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Manages a user session and its tokens."""

    reset_password_token_secret = settings.users_secret
    verification_token_secret = settings.users_secret


async def get_user_db(
    session: AsyncSession = Depends(get_db_session),
) -> SQLAlchemyUserDatabase:
    """
    Yield a SQLAlchemyUserDatabase instance.

    :param session: asynchronous SQLAlchemy session.
    :yields: instance of SQLAlchemyUserDatabase.
    """
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> UserManager:
    """
    Yield a UserManager instance.

    :param user_db: SQLAlchemy user db instance
    :yields: an instance of UserManager.
    """
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """
    Return a JWTStrategy in order to instantiate it dynamically.

    :returns: instance of JWTStrategy with provided settings.
    """
    return JWTStrategy(secret=settings.users_secret, lifetime_seconds=None)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_jwt = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

backends = [
    auth_jwt,
]

api_users = FastAPIUsers[User, uuid.UUID](get_user_manager, backends)

current_active_user = api_users.current_user(active=True)
