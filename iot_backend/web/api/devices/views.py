from fastapi import APIRouter, status
from fastapi.param_functions import Depends

from iot_backend.db.dao.device_dao import DeviceDAO
from iot_backend.db.models.users import User, current_active_user
from iot_backend.web.api.devices.schema import DeviceDTO, DeviceInputDTO

router = APIRouter()


@router.get(
    "/", dependencies=[Depends(current_active_user)], response_model=list[DeviceDTO]
)
async def get_devices(
    user: User = Depends(current_active_user),
    limit: int = 10,
    offset: int = 0,
    device_dao: DeviceDAO = Depends(),
) -> list[DeviceDTO]:
    """
    Retrieve all device objects from the database.

    :param limit: limit of device objects, defaults to 10.
    :param offset: offset of device objects, defaults to 0.
    :param device_dao: DAO for device models.
    :return: list of device objects from database.
    """
    return await device_dao.get_all_devices(user_id=user.id, limit=limit, offset=offset)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(current_active_user)],
)
async def create_device(
    new_device_object: DeviceInputDTO,
    device_dao: DeviceDAO = Depends(),
    user: User = Depends(current_active_user),
) -> None:
    """
    Creates device model in the database.

    :param new_device_object: new device model item.
    :param device_dao: DAO for device models.
    """
    await device_dao.create_device_model(
        user_id=user.id,
        org_id=user.organization_id,
        type=new_device_object.type,
        name=new_device_object.name,
        meta_data=new_device_object.meta_data,
        is_configured=new_device_object.is_configured,
        mainflux_thing_uuid=new_device_object.mainflux_thing_uuid,
        mainflux_thing_secret=new_device_object.mainflux_thing_secret,
        parent_id=new_device_object.parent_id,
    )


@router.get(
    "/{device_id}",
    dependencies=[Depends(current_active_user)],
    response_model=DeviceDTO,
)
async def get_device(
    device_id: int,
    device_dao: DeviceDAO = Depends(),
    user: User = Depends(current_active_user),
) -> DeviceDTO:
    """
    Retrieve a specific device object from the database by its id.

    :param device_id: id of the device object.
    :param device_dao: DAO for device models.
    :return: device object from database.
    """
    response = await device_dao.get_device(device_id=device_id, user_id=user.id)
    return response


@router.patch(
    "/{device_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(current_active_user)],
)
async def update_device_metadata(
    device_id: int,
    new_metadata: dict,
    device_dao: DeviceDAO = Depends(),
    user: User = Depends(current_active_user),
):
    """
    Update the metadata of a specific device object in the database.

    :param device_id: id of the device object.
    :param new_metadata: new metadata for the device.
    :param device_dao: DAO for device models.
    """
    await device_dao.update_device_metadata(
        device_id=device_id, user_id=user.id, metadata=new_metadata
    )


@router.patch(
    "/{device_id}/link",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(current_active_user)],
)
async def link_device_to_user(
    device_id: int,
    device_dao: DeviceDAO = Depends(),
    user: User = Depends(current_active_user),
):
    """
    Link a device to a user.

    :param user_id: id of the user.
    :param device_id: id of the device.
    :param device_dao: DAO for device models.
    """
    await device_dao.patch_device_user_id(user_id=user.id, device_id=device_id)
