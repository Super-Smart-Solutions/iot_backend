from typing import List

from fastapi import APIRouter, HTTPException, Path, Query, status
from fastapi.param_functions import Depends
from pydantic import BaseModel

from iot_backend.db.dao.organization_dao import OrganizationDAO
from iot_backend.db.models.organization import Organization
from iot_backend.db.models.users import current_active_user
from iot_backend.web.api.organizations.schema import (
    OrganizationResponse,
    OrganizationCreate,
)

router = APIRouter()


class NotFoundError(BaseModel):
    detail: str = "The requested resource was not found"


class UnauthorizedError(BaseModel):
    detail: str = "Unauthorized access"


class BadRequest(BaseModel):
    detail: str = "Name already exists"


@router.get(
    "/",
    response_model=List[OrganizationResponse],
    dependencies=[Depends(current_active_user)],
)
async def get_organizations(
    limit: int = Query(10, description="Limit the number of organizations returned"),
    offset: int = Query(0, description="Offset for pagination"),
    organization_dao: OrganizationDAO = Depends(),
) -> List[Organization]:
    """
    #TODO access should be for admins only.
    Retrieve all organization objects from the database.

    :param limit: limit of organization objects, defaults to 10.
    :param offset: offset of organization objects, defaults to 0.
    :param organization_dao: DAO for organization models.
    :return: list of organization objects from database.
    """
    return await organization_dao.list(limit=limit, offset=offset)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=OrganizationResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequest,
            "description": "Name already exists",
        }
    },
    dependencies=[Depends(current_active_user)],
)
async def create_organization(
    new_organization_object: OrganizationCreate,
    organization_dao: OrganizationDAO = Depends(),
) -> OrganizationResponse:
    """
    #TODO access should be for admins only.

    Creates organization model in the database.

    :param new_organization_object: new organization model item.
    :param organization_dao: DAO for organization models.
    """
    await organization_dao.create(new_organization_object.name, new_organization_object)


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": NotFoundError,
            "description": "Resource not found",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": UnauthorizedError,
            "description": "Unauthorized access",
        },
    },
    dependencies=[Depends(current_active_user)],
)
async def get_organization(
    organization_id: int = Path(
        ..., description="ID of the organization to retrieve"
    ),  # Path param with description
    organization_dao: OrganizationDAO = Depends(),
):
    """
    Retrieve an organization by ID.
    """
    organization = await organization_dao.get(id=organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return organization


@router.delete("/{organization_id}", response_model=OrganizationResponse)
async def delete_organization(
    organization_id: int = Path(..., description="ID of the organization to delete"),
):
    """
    Delete an organization by ID.
    """
    dao = OrganizationDAO()
    deleted_organization = await dao.delete(id=organization_id)
    if not deleted_organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return deleted_organization
