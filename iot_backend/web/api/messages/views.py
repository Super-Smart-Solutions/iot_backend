from fastapi import APIRouter, Depends

from iot_backend.db.dao.message_dao import MessageDAO
from iot_backend.web.api.messages.schema import MessageCreate

router = APIRouter()


@router.post("/{channel_id}/messages")
async def send_message(
    channel_id: str, message: MessageCreate, message_dao: MessageDAO = Depends()
):
    """Creates Message model in the database."""
    return await message_dao.create(channel_id=channel_id, schema=message)


@router.get("/{channel_id}/messages")
async def get_messages(channel_id: str, message_dao: MessageDAO = Depends()):
    """Retrieves messages sent to single channel"""
    return await message_dao.get_by("channel_id", channel_id)
