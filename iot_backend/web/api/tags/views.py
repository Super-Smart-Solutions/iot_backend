from typing import Optional

from fastapi import APIRouter, Depends, status

from iot_backend.db.dao.tag_dao import TagDAO
from iot_backend.db.models.users import User, current_active_user
from iot_backend.web.api.tags.schema import TagDTO, TagInputDTO

router = APIRouter()


@router.get(
    "/", dependencies=[Depends(current_active_user)], response_model=list[TagDTO]
)
async def get_tags(
    device_id: Optional[int] = None,
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    user: User = Depends(current_active_user),
    tag_dao: TagDAO = Depends(),
) -> list[TagDTO]:
    """
    Retrieve all tag objects from the database.

    :param device_id: ID of the device (optional).
    :param limit: limit of tag objects, defaults to 10.
    :param offset: offset of tag objects, defaults to 0.
    :param tag_dao: DAO for tag models.
    :return: list of tag objects from database.
    """
    return await tag_dao.get_all_tags(
        user_id=user.id, limit=limit, offset=offset, device_id=device_id
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(current_active_user)],
)
async def create_tag(
    new_tag_object: TagInputDTO,
    tag_dao: TagDAO = Depends(),
    user: User = Depends(current_active_user),
) -> None:
    """
    Creates tag model in the database.

    :param new_tag_object: new tag model item.
    :param tag_dao: DAO for tag models.
    """
    return await tag_dao.create_tag(user_id=user.id, new_tag=new_tag_object)


@router.post(
    "/bulk",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(current_active_user)],
)
async def create_tags(
    new_tags: list[TagInputDTO],
    tag_dao: TagDAO = Depends(),
    user: User = Depends(current_active_user),
) -> None:
    """
    Creates multiple tag models in the database.

    :param new_tags: list of new tag model items.
    :param tag_dao: DAO for tag models.
    """
    return await tag_dao.create_tags(user_id=user.id, tags=new_tags)


@router.get(
    "/{tag_id}", dependencies=[Depends(current_active_user)], response_model=TagDTO
)
async def get_tag(
    tag_id: int,
    tag_dao: TagDAO = Depends(),
    user: User = Depends(current_active_user),
) -> TagDTO:
    """
    Retrieve a specific tag object from the database by its id.

    :param tag_id: id of the tag object.
    :param tag_dao: DAO for tag models.
    :return: tag object from database.
    """
    response = await tag_dao.get_tag(tag_id=tag_id, user_id=user.id)
    return response


@router.patch(
    "/{tag_id}/show",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(current_active_user)],
)
async def show(
    tag_id: int,
    tag_dao: TagDAO = Depends(),
    user: User = Depends(current_active_user),
):
    """
    Update a specific tag object in the database.

    :param tag_id: id of the tag object.
    :param tag_dao: DAO for tag models.
    """
    return await tag_dao.update_tag(tag_id=tag_id, graphed=True, user_id=user.id)


@router.patch(
    "/{tag_id}/hide",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(current_active_user)],
)
async def hide(
    tag_id: int,
    tag_dao: TagDAO = Depends(),
    user: User = Depends(current_active_user),
):
    """
    Update a specific tag object in the database.

    :param tag_id: id of the tag object.
    :param tag_dao: DAO for tag models.
    """
    return await tag_dao.update_tag(tag_id=tag_id, graphed=False, user_id=user.id)


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(current_active_user)],
)
async def delete_tag(
    tag_id: int,
    tag_dao: TagDAO = Depends(),
    user: User = Depends(current_active_user),
) -> None:
    """
    Delete a specific tag object from the database.

    :param tag_id: id of the tag object.
    :param tag_dao: DAO for tag models.
    """
    return await tag_dao.delete_tag(tag_id=tag_id, user_id=user.id)


@router.delete(
    "/delete/bulk",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(current_active_user)],
)
async def remove_tags(
    tag_ids: list[int],
    tag_dao: TagDAO = Depends(),
    user: User = Depends(current_active_user),
) -> None:
    return await tag_dao.delete_tags(tag_ids=tag_ids, user_id=user.id)
