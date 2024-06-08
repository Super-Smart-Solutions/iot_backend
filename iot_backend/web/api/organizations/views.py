from typing import List

from fastapi import APIRouter, status
from fastapi.param_functions import Depends

from iot_backend.db.dao.organization_dao import OrganizationDAO
from iot_backend.db.models.organization import Organization
from iot_backend.db.models.users import current_active_user
from iot_backend.web.api.organizations.schema import (
    OrganizationDTO,
    OrganizationInputDTO,
)

router = APIRouter()


@router.get(
    "/", response_model=List[OrganizationDTO], dependencies=[Depends(current_active_user)]
)
async def get_organizations(
    limit: int = 10,
    offset: int = 0,
    organization_dao: OrganizationDAO = Depends(),
) -> List[Organization]:
    """
    Retrieve all organization objects from the database.

    :param limit: limit of organization objects, defaults to 10.
    :param offset: offset of organization objects, defaults to 0.
    :param organization_dao: DAO for organization models.
    :return: list of organization objects from database.
    """
    return await organization_dao.get_all_organizations(limit=limit, offset=offset)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(current_active_user)]
)
async def create_organization(
    new_organization_object: OrganizationInputDTO,
    organization_dao: OrganizationDAO = Depends(),
) -> None:
    """
    Creates organization model in the database.

    :param new_organization_object: new organization model item.
    :param organization_dao: DAO for organization models.
    """
    await organization_dao.create_organization_model(name=new_organization_object.name)
