from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from iot_backend.db.dao.base_dao import BaseDAO
from iot_backend.db.dependencies import get_db_session
from iot_backend.db.models.organization import Organization
from iot_backend.web.api.organizations.schema import OrganizationCreate


class OrganizationDAO(BaseDAO[Organization]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        super().__init__(Organization, session)

    async def create(self, name: str, schema: OrganizationCreate) -> Organization:
        """
        Add single organization to session.

        :param name: name of an organization.
        :param schema: The Pydantic schema representing the organization data.
        """
        existing_organization = await self.filter(name=name)
        if existing_organization:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization name must be unique",
            )
        return await super().create(schema=schema)

    async def filter(
        self,
        name: Optional[str] = None,
    ) -> List[Organization]:
        """
        Get specific organization model.

        :param name: name of organization instance.
        :return: organization models.
        """
        query = select(self.model)
        if name:
            query = query.where(self.model.name == name)
        rows = await self.session.execute(query)
        return list(rows.scalars().all())
