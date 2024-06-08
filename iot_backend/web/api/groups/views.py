from typing import List

from fastapi import APIRouter, status
from fastapi.param_functions import Depends

from iot_backend.db.dao.group_dao import GroupDAO
from iot_backend.db.models.group import Group
from iot_backend.db.models.users import current_active_user
from iot_backend.web.api.groups.schema import GroupDTO, GroupInputDTO

router = APIRouter()


@router.get(
    "/", response_model=List[GroupDTO], dependencies=[Depends(current_active_user)]
)
async def get_groups(
    limit: int = 10,
    offset: int = 0,
    group_dao: GroupDAO = Depends(),
) -> List[Group]:
    """
    Retrieve all group objects from the database.

    :param limit: limit of group objects, defaults to 10.
    :param offset: offset of group objects, defaults to 0.
    :param group_dao: DAO for group models.
    :return: list of group objects from database.
    """
    return await group_dao.get_all_groups(limit=limit, offset=offset)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(current_active_user)]
)
async def create_group(
    new_group_object: GroupInputDTO,
    group_dao: GroupDAO = Depends(),
) -> None:
    """
    Creates group model in the database.

    :param new_group_object: new group model item.
    :param group_dao: DAO for group models.
    """
    await group_dao.create_group_model(
        name=new_group_object.name,
        organization_id=new_group_object.organization_id,
    )
