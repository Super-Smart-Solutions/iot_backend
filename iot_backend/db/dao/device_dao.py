from typing import Any, List, Optional, Union
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from iot_backend.db.dependencies import get_db_session
from iot_backend.db.models.device import Device


class DeviceDAO:
    """Class for accessing device table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_by(
        self, field: str, value: Any, unique: bool = False
    ) -> Optional[Union[Device, List[Device]]]:
        """
        Get Devices based on a specific criteria.

        Args:
            field (str): The field to filter Devices.
            value (Any): The value to match for the field.
            unique (bool, optional): Flag indicating if the field is expected to be unique. Defaults to False.


        Returns:
            Optional[Union[ModelType, List[ModelType]]]:
            - A single model instance if unique is True and a match is found.
            - A list of model instances if unique is False and matches are found.
            - None if no match is found.
        """
        query = select(Device)
        if (
            unique
            and hasattr(Device, field)
            and getattr(Device.__table__.columns[field], "unique", False)
        ):
            query = query.filter_by(**{field: value})
            row = await self.session.scalars(query)
            response = row.one_or_none()
        else:
            query = query.where(getattr(Device, field) == value)
            row = await self.session.scalars(query)
            response = row.all()
        if not response or None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Device Not Found."
            )
        return response

    async def get_device(self, device_id: int, user_id: UUID) -> Optional[Device]:
        """
        Get a Device by its ID.

        Args:
            device_id (int): The ID of the Device to retrieve.
            user_id (UUID): The ID of the user.

        Returns:
            Optional[Device]: The Device with the specified ID, or None if not found.
        """
        device = await self.get_by(field="id", value=device_id, unique=True)
        if device.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to access this data.",
            )
        return device

    async def create_device_model(
        self,
        user_id: UUID,
        org_id: int,
        type: str,
        name: Optional[str] = None,
        meta_data: Optional[dict[str, Any]] = None,
        is_configured: Optional[bool] = False,
        mainflux_thing_uuid: Optional[UUID] = None,
        mainflux_thing_secret: Optional[UUID] = None,
        parent_id: Optional[int] = None,
    ) -> None:
        """
        Add single device to session.

        :param user_id: user id of the device
        :param org_id: organization id of the device
        :param type: type of the device
        :param name: name of a device.
        :param meta_data: meta data of the device
        :param is_configured: whether the device is configured
        :param mainflux_thing_uuid: mainflux thing uuid of the device
        :param mainflux_thing_secret: mainflux thing secret of the device
        :param parent_id: parent id of the device

        """
        self.session.add(
            Device(
                user_id=user_id,
                org_id=org_id,
                type=type,
                name=name,
                meta_data=meta_data,
                is_configured=is_configured,
                mainflux_thing_uuid=mainflux_thing_uuid,
                mainflux_thing_secret=mainflux_thing_secret,
                parent_id=parent_id,
            )
        )

    async def get_all_devices(
        self, user_id: UUID, limit: int, offset: int
    ) -> list[Device]:
        """
        Get all device models with limit/offset pagination.

        :param user_id: user ID.
        :param limit: limit of device.
        :param offset: offset of device.
        :return: stream of device.
        """
        query = (
            select(Device).where(Device.user_id == user_id).offset(offset).limit(limit)
        )
        raw_devices = await self.session.scalars(query)
        devices = raw_devices.all()

        if not devices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No Devices Found."
            )
        return devices

    async def update_device_metadata(
        self, device_id: int, user_id: UUID, metadata: dict
    ):
        """
        Update the metadata of a device model.

        :param user_id: user ID.
        :param device_id: ID of the device model.
        :param metadata: new metadata for the device model.
        :return: updated device model or None if not found.
        """
        query = select(Device).where(Device.id == device_id)
        row = await self.session.scalars(query)
        device = row.one_or_none()

        if device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Device not found"
            )

        if device.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        device.meta_data = metadata
        return device

    async def patch_device_user_id(self, device_id: int, user_id: UUID):
        """
        Update the user_id of a device model.

        :param device_id: ID of the device model.
        :param user_id: new user_id for the device model.
        :return: updated device model or None if not found.
        """
        query = select(Device).where(Device.id == device_id)
        row = await self.session.scalars(query)
        device = row.one_or_none()

        if device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Device not found"
            )
        if device.user_id is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Device already linked to a user.",
            )

        device.user_id = user_id
        return device

    async def delete_device(self, device_id: int, user_id: UUID) -> None:
        """
        Deletes a Device by its ID, raising a 403 Forbidden if user lacks permission or 404 Not Found if not found.

        Args:
            device_id (int): ID of the Device to be deleted.
            user_id (UUID): User ID for permission check.
        """
        device = await self.get_by(field="id", value=device_id, unique=True)

        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Device not found"
            )

        if device.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to access this data.",
            )

        await self.session.delete(device)
