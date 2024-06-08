from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from iot_backend.db.dependencies import get_db_session
from iot_backend.db.models.group import Group


class GroupDAO:
    """Class for accessing group table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_group_model(self, name: str, organization_id: int) -> None:
        """
        Add single group to session.

        :param name: name of an group.
        :param organization_id: id of the organization
        """

        # Check if there is a group by the same name.
        existing_group = await self.filter(name=name)
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group name must be unique.",
            )

        self.session.add(Group(name=name, organization_id=organization_id))

    async def get_all_groups(self, limit: int, offset: int) -> List[Group]:
        """
        Get all group models with limit/offset pagination.

        :param limit: limit of group.
        :param offset: offset of group.
        :return: stream of group.
        """
        raw_organizations = await self.session.execute(
            select(Group).limit(limit).offset(offset),
        )

        return list(raw_organizations.scalars().fetchall())

    async def filter(
        self,
        name: Optional[str] = None,
    ) -> List[Group]:
        """
        Get specific group model.

        :param name: name of group instance.
        :return: group models.
        """
        query = select(Group)
        if name:
            query = query.where(Group.name == name)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())

    async def update_group(self, group_id: int, name: str) -> Optional[Group]:
        """
        Update the name of an group model.

        :param group_id: ID of the group model.
        :param name: new name for the group model.
        :return: updated group model or None if not found.
        """
        query = select(Group).where(Group.id == group_id)
        row = await self.session.execute(query)
        group = row.scalar_one_or_none()
        if group:
            group.name = name
        return group

    async def delete_group(self, group_id: int) -> Optional[Group]:
        """
        Delete an group model by its ID.

        :param group_id: ID of the group model.
        :return: deleted group model or None if not found.
        """
        query = select(Group).where(Group.id == group_id)
        row = await self.session.execute(query)
        group = row.scalar_one_or_none()
        if group:
            self.session.delete(group)
        return group
