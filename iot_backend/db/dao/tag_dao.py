from typing import Any, List, Optional, Union
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from iot_backend.db.dependencies import get_db_session
from iot_backend.db.models.device import Device
from iot_backend.db.models.tag import Tag
from iot_backend.web.api.tags.schema import TagInputDTO


class TagDAO:
    """Class for accessing tag table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_by(
        self, field: str, value: Any, unique: bool = False
    ) -> Optional[Union[Tag, List[Tag]]]:
        """
        Get Tags based on a specific criteria.

        Args:
            field (str): The field to filter Tags.
            value (Any): The value to match for the field.
            unique (bool, optional): Flag indicating if the field is expected to be unique. Defaults to False.


        Returns:
            Optional[Union[ModelType, List[ModelType]]]:
            - A single model instance if unique is True and a match is found.
            - A list of model instances if unique is False and matches are found.
            - None if no match is found.
        """
        query = select(Tag)
        if (
            unique
            and hasattr(Tag, field)
            and getattr(Tag.__table__.columns[field], "unique", False)
        ):
            query = query.filter_by(**{field: value})
            row = await self.session.scalars(query)
            response = row.one_or_none()
        else:
            query = query.where(getattr(Tag, field) == value)
            row = await self.session.scalars(query)
            response = row.all()
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag Not Found."
            )
        return response

    async def get_tag(self, tag_id: int, user_id: UUID) -> Optional[Tag]:
        """
        Retrieves a Tag by its ID.

        Args:
            tag_id (int): ID of the Tag to be retrieved.

        Returns:
            Optional[Tag]: The Tag object or None if not found.
        """
        tag = await self.get_by(field="id", value=tag_id, unique=True)
        if tag.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to access this data.",
            )
        return tag

    async def create_tag(
        self,
        user_id: UUID,
        new_tag: TagInputDTO,
    ) -> None:
        """
        Add a single tag to the session.

        :param user_id: ID of the user adding the tag.
        :param new_tag: TagInputDTO object containing the details of the new tag.
        """
        device = (
            await self.session.scalars(
                select(Device).where(Device.id == new_tag.device_id)
            )
        ).one_or_none()
        if device and device.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to add a tag to this device.",
            )
        self.session.add(
            Tag(
                name=new_tag.name,
                label=new_tag.label,
                target=new_tag.target,
                unit=new_tag.unit,
                multiplier=new_tag.multiplier,
                mask=new_tag.mask,
                graphed=new_tag.graphed,
                user_id=user_id,
                device_id=new_tag.device_id,
            )
        )

    async def create_tags(self, user_id: UUID, tags: List[TagInputDTO]) -> None:
        """
        Add one or more tags to the session.

        :param user_id: the ID of the user adding the tags.
        :param tags: a list of TagInputDTO objects representing the tags.
        """
        for tag_data in tags:
            await self.create_tag(user_id=user_id, new_tag=tag_data)
        return None

    async def get_all_tags(
        self, user_id: UUID, limit: int, offset: int, device_id: Optional[int] = None
    ) -> List[Tag]:
        """
        Get all tags with limit/offset pagination.
        :param user_id: user ID.
        :param limit: limit of tags.
        :param offset: offset of tags.
        :param device_id: device ID.
        :return: list of tags.
        """
        query = select(Tag).where(Tag.user_id == user_id)
        if device_id:
            device = await self.session.get(Device, device_id)
            if not device or device.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this device's tags.",
                )
            query = query.where(Tag.device_id == device_id)
        query = query.offset(offset).limit(limit)
        raw_tags = await self.session.scalars(query)
        tags = raw_tags.all()

        if not tags:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There are no Tags for this device.",
            )
        return tags

    async def update_tag(
        self, tag_id: int, graphed: bool, user_id: UUID
    ) -> Optional[Tag]:
        """
        Updates the 'graphed' attribute of a Tag.

        Args:
            tag_id (int): ID of the Tag to be updated.
            graphed (bool): New value for the 'graphed' attribute.

        Returns:
            Optional[Tag]: The updated Tag object or None if not found.
        """

        tag = await self.get_by(field="id", value=tag_id, unique=True)
        if tag and tag.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to access this data.",
            )
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        tag.graphed = graphed
        return tag

    async def delete_tag(self, tag_id: int, user_id: UUID) -> None:
        """
        Deletes a Tag by its ID, raising a 403 Forbidden if user lacks permission or 404 Not Found if not found.

        Args:
            tag_id (int): ID of the Tag to be deleted.
            user_id (UUID): User ID for permission check.
        """
        tag = await self.get_by(field="id", value=tag_id, unique=True)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
            )

        if tag.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to access this data.",
            )

        await self.session.delete(tag)

    async def delete_tags(self, tag_ids: list[int], user_id: UUID) -> None:
        """
        Deletes tags based on a list of IDs and performs user permission checks.

        :param tag_ids: List of tag IDs to delete.
        :param user_id: ID of the user performing the deletion.
        :raises HTTPException: If a tag is not found or the user lacks permission to delete it.
        """

        query = delete(Tag).where(Tag.id.in_(tag_ids))  # Delete matching tags

        # Apply user permission check using a subquery
        permission_check = (
            select(1)
            .select_from(Tag)
            .where(Tag.id.in_(tag_ids))
            .where(Tag.user_id == user_id)
        )
        query = query.where(exists(permission_check))  # Ensure tags belong to the user

        deleted_count = await self.session.execute(query)
        deleted = deleted_count.rowcount

        if deleted != len(tag_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission to delete all tags. {deleted} tags deleted.",
            )

        return deleted
