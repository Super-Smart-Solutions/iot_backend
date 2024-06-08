from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from iot_backend.db.dependencies import get_db_session
from iot_backend.db.models.organization import Organization


class OrganizationDAO:
    """Class for accessing organization table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_organization_model(self, name: str) -> None:
        """
        Add single organization to session.

        :param name: name of an organization.
        """
        # Check if there is a organization by the same name.
        existing_organization = await self.filter(name=name)
        if existing_organization:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization name must be unique",
            )
        self.session.add(Organization(name=name))

    async def get_all_organizations(
        self, limit: int, offset: int
    ) -> List[Organization]:
        """
        Get all organization models with limit/offset pagination.

        :param limit: limit of organizations.
        :param offset: offset of organizations.
        :return: stream of organizations.
        """
        raw_organizations = await self.session.execute(
            select(Organization).limit(limit).offset(offset),
        )

        return list(raw_organizations.scalars().fetchall())

    async def filter(
        self,
        name: Optional[str] = None,
    ) -> List[Organization]:
        """
        Get specific organization model.

        :param name: name of organization instance.
        :return: organization models.
        """
        query = select(Organization)
        if name:
            query = query.where(Organization.name == name)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())

    async def update_organization(
        self, organization_id: int, name: str
    ) -> Optional[Organization]:
        """
        Update the name of an organization model.

        :param organization_id: ID of the organization model.
        :param name: new name for the organization model.
        :return: updated organization model or None if not found.
        """
        query = select(Organization).where(Organization.id == organization_id)
        row = await self.session.execute(query)
        organization = row.scalar_one_or_none()
        if organization:
            organization.name = name
        return organization

    async def delete_organization(self, organization_id: int) -> Optional[Organization]:
        """
        Delete an organization model by its ID.

        :param organization_id: ID of the organization model.
        :return: deleted organization model or None if not found.
        """
        query = select(Organization).where(Organization.id == organization_id)
        row = await self.session.execute(query)
        organization = row.scalar_one_or_none()
        if organization:
            self.session.delete(organization)
        return organization
