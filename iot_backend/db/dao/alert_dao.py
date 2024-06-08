from typing import Any, List, Optional, Union
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from iot_backend.db.dependencies import get_db_session
from iot_backend.db.models.alert import Alert
from iot_backend.db.models.device import Device


class AlertDAO:
    """Class for accessing alert table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_by(
        self, field: str, value: Any, unique: bool = False
    ) -> Optional[Union[Alert, List[Alert]]]:
        """
        Get Alerts based on a specific criteria.

        Args:
            field (str): The field to filter Alerts.
            value (Any): The value to match for the field.
            unique (bool, optional): Flag indicating if the field is expected to be unique. Defaults to False.


        Returns:
            Optional[Union[ModelType, List[ModelType]]]:
            - A single model instance if unique is True and a match is found.
            - A list of model instances if unique is False and matches are found.
            - None if no match is found.
        """
        query = select(Alert)
        if (
            unique
            and hasattr(Alert, field)
            and getattr(Alert.__table__.columns[field], "unique", False)
        ):
            query = query.filter_by(**{field: value})
            row = await self.session.scalars(query)
            response = row.one_or_none()
        else:
            query = query.where(getattr(Alert, field) == value)
            row = await self.session.scalars(query)
            response = row.all()
        # if not response:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail="Alert Not Found."
        #     )
        return response

    async def get_alert(self, alert_id: int, user_id: UUID) -> Optional[Alert]:
        """
        Retrieves a Alert by its ID.

        Args:
            Alert_id (int): ID of the Alert to be retrieved.

        Returns:
            Optional[Alert]: The Alert object or None if not found.
        """
        alert = await self.get_by(field="id", value=alert_id, unique=True)
        if not alert or alert.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to access this data.",
            )
        return alert

    async def create_alert_model(
        self,
        name: str,
        comparator: str,
        threshold: float,
        status: str,
        check_external_id: str,
        check_external_message_template: str,
        device_id: int,
        user_id: UUID,
    ) -> None:
        """
        Add single alert to session.

        Args:
            name (str): Name of an alert.
            comparator (str): Comparator for the alert.
            threshold (float): Threshold for the alert.
            status (str): Status of the alert.
            device_id (int): Device ID associated with the alert.
            user_id (str): User ID associated with the alert.
            check_external_id (str): External ID for the check associated with the alert.
            check_external_message_template (str): Message template for the check associated with the alert.

        Raises:
            HTTPException: If the alert name is not unique.
        """

        exists = await self.get_by(field="name", value=name, unique=True)
        if exists is not None:
            raise HTTPException(
                status_code=400,
                detail="Alert name must be unique.",
            )
        self.session.add(
            Alert(
                name=name,
                comparator=comparator,
                threshold=threshold,
                status=status,
                check_external_id=check_external_id,
                check_external_message_template=check_external_message_template,
                device_id=device_id,
                user_id=user_id,
            )
        )

    async def get_all_alerts(
        self, user_id: UUID, limit: int, offset: int, device_id: Optional[int] = None
    ) -> list[Alert]:
        """
        Get all alert models with limit/offset pagination.

        :param limit: limit of alerts.
        :param offset: offset of alerts.
        :param user_id: user ID.
        :param device_id: device ID.
        :return: list of tags.
        """
        query = select(Alert).where(Alert.user_id == user_id)
        if device_id:
            device = await self.session.get(Device, device_id)
            if not device or device.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this device's alerts.",
                )
            query = query.where(Alert.device_id == device_id)
        query = query.offset(offset).limit(limit)
        raw_alerts = await self.session.scalars(query)
        alerts = raw_alerts.all()

        if not alerts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There are no Alerts for this device.",
            )
        return alerts

    async def disable_alert(self, alert_id: int, user_id: UUID) -> None:
        """
        Disables an alert with the given alert_id.

        Parameters:
        - alert_id (int): The unique identifier of the alert to be disabled.
        - user_id (UUID): The ID of the user for permission check.

        Raises:
        - HTTPException: If the alert with the given alert_id is not found or if the alert is already disabled.

        Returns:
        - None
        """
        alert: Alert = await self.get_by(field="id", value=alert_id, unique=True)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found.",
            )
        if alert.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        if alert.status == "disabled":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        alert.status = "disabled"

    async def enable_alert(self, alert_id: int, user_id: UUID) -> None:
        """
        Enables an alert with the given alert_id.

        Parameters:
        - alert_id (int): The unique identifier of the alert to be enabled.
        - user_id (UUID): The ID of the user for permission check.

        Raises:
        - HTTPException: If the alert with the given alert_id is not found or if the alert is already enabled.

        Returns:
        - None
        """
        alert: Alert = await self.get_by(field="id", value=alert_id, unique=True)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found.",
            )
        if alert.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        if alert.status == "enabled":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        alert.status = "enabled"

    async def delete_alert(self, alert_id: int, user_id: UUID) -> None:
        """
        Deletes an alert with the given alert_id.

        Parameters:
        - alert_id (int): The unique identifier of the alert to be deleted.
        - user_id (UUID): The ID of the user for permission check.

        Raises:
        - HTTPException: If the alert with the given alert_id is not found.

        Returns:
        - None
        """
        alert: Alert = await self.get_by(field="id", value=alert_id, unique=True)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found.",
            )
        if alert.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return await self.session.delete(alert)

    # async def disable_all_alerts(self, user_id: UUID) -> None:
    #     """
    #     Disables all alerts.

    #     Parameters:
    #     - user_id (UUID): The ID of the user.

    #     Raises:
    #     - HTTPException: If there are no alerts to disable.

    #     Returns:
    #     - None
    #     """
    #     alerts = await self.get_by(field="status", value="enabled")
    #     if not alerts:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="There are no enabled alerts to disable.",
    #         )
    #     for alert in alerts:
    #         self.disable_alert(alert.id, user_id=user_id)
