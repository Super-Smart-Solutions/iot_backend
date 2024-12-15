from fastapi import APIRouter, Depends

from iot_backend.db.dao.device_dao import DeviceDAO
from iot_backend.db.dao.message_dao import MessageDAO
from iot_backend.db.dao.tag_dao import TagDAO
from iot_backend.db.models.device import Device
from iot_backend.db.models.tag import Tag
from iot_backend.web.api.messages.schema import MessageCreate
from iot_backend.db.models.users import User, current_active_user


router = APIRouter()


@router.post("/{tag_id}/messages")
async def send_message(
    tag_id: int,
    device_id: int,
    message: MessageCreate,
    message_dao: MessageDAO = Depends(),
    tag_dao: TagDAO = Depends(),
    device_dao: DeviceDAO = Depends(),
    user: User = Depends(current_active_user),

):
    """Creates Message model in the database."""
    # TODO Valid id/name helper function

    tag: Tag = tag_dao.get_tag(tag_id, user.id)
    device: Device = device_dao.get_device(device_id, user.id)
    message.publisher = device.mainflux_thing_uuid
    message.channel_id = tag.mainflux_channel_uuid

    return await message_dao.create(tag_id=tag.id, schema=message)


@router.get("/{tag_id}/messages")
async def read_messages(
    tag_id: int,
    message_dao: MessageDAO = Depends(),
    tag_dao: TagDAO = Depends(),
    user: User = Depends(current_active_user),
):
    """Retrieves messages sent to single channel"""
    tag: Tag = tag_dao.get_tag(tag_id, user.id)
    return await message_dao.get_by("tag_id", tag.id)
