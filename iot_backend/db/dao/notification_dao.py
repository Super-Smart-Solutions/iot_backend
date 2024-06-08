from typing import Any, List, Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from iot_backend.db.dependencies import get_db_session
from iot_backend.db.models.notification import Notification


class NotificationDAO:
    """Class for accessing notification table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_by(
        self,
        field: str,
        value: Any,
    ) -> Optional[Notification]:
        """
        Get Notifications based on a specific criteria.

        Args:
            field (str): The field to filter Notifications.
            value (Any): The value to match for the field.

        Returns:
            list[Notification]: List of Notifications that match the criteria.
        """
        query = select(Notification).where(getattr(Notification, field) == value)
        rows = await self.session.scalars(query)
        return rows.one_or_none()

    async def create_notification(
        self,
        message: str,
        level: str,
        check_id: str,
        notification_endpoint_id: str,
        notification_rule_id: str,
        alert_id: int,
        device_id: int,
        user_id: str,
    ) -> None:
        """
        Add single notification to session.
        :param message: message of the notification.
        :param level: level of the notification.
        :param check_id: check_id of the notification.
        :param notification_endpoint_id: notification_endpoint_id of the notification.
        :param notification_rule_id: notification_rule_id of the notification.
        :param alert_id: alert_id of the notification.
        :param device_id: device_id of the notification.
        :param user_id: user_id of the notification.
        """
        self.session.add(
            Notification(
                message=message,
                level=level,
                check_id=check_id,
                notification_endpoint_id=notification_endpoint_id,
                notification_rule_id=notification_rule_id,
                alert_id=alert_id,
                device_id=device_id,
                user_id=user_id,
            )
        )

    async def get_all_notifications(
        self,
        limit: int,
        offset: int,
        user_id: UUID,
        device_id: Optional[int] = None,
        alert_id: Optional[int] = None,
    ) -> list[Notification]:
        """
        Get all notification models with limit/offset pagination and optional device_id and/or alert_id filters.

        :param limit: limit of notifications.
        :param offset: offset of notifications.
        :param device_id: optional device ID filter.
        :param alert_id: optional alert ID filter.
        :return: stream of notifications.
        """
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )

        if device_id is not None:
            query = query.where(Notification.device_id == device_id)

        if alert_id is not None:
            query = query.where(Notification.alert_id == alert_id)

        raw_notifications = await self.session.scalars(query)

        return list(raw_notifications.all())

    async def filter(
        self,
        name: Optional[str] = None,
    ) -> list[Notification]:
        """
        Get specific notification model.

        :param name: name of notification instance.
        :return: notification models.
        """
        query = select(Notification)
        if name:
            query = query.where(Notification.name == name)
        rows = await self.session.scalars(query)
        return list(rows.all())
