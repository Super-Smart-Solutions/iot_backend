from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.param_functions import Depends
from mainflux_client.models.messages_page import MessagesPage
from mainflux_client.rest import ApiException
from pydantic import StrictStr

from iot_backend.db.dao.device_dao import DeviceDAO
from iot_backend.db.models.device import Device
from iot_backend.db.models.users import User, current_active_user
from iot_backend.services.mainflux import get_channels_api, get_reader_api
from iot_backend.settings import settings

router = APIRouter()


@router.get(
    "/{tag_name}/records",
    # response_model=MessagesPage,
    dependencies=[Depends(current_active_user)],
)
async def receive(
    tag_name: StrictStr,
    device_id: int,
    user: User = Depends(current_active_user),
    device_dao: DeviceDAO = Depends(),
    limit: Annotated[
        Optional[Annotated[int, Query(le=100, ge=1)]],
        Query(description="Size of the subset to retrieve."),
    ] = None,
    offset: Annotated[
        Optional[Annotated[int, Query(ge=0)]],
        Query(description="Number of items to skip during retrieval."),
    ] = None,
):
    """
    Receives records from a channel.

    Args:
        tag_id (str): Unique channel identifier (required).
        device_id (str): Device identifier (required).
        limit (int): Size of the subset to retrieve (required).
        offset (int): Number of items to skip during retrieval (required).

    Returns:
        MessagesPage: Returns the result object.

    Raises:
        HTTPException: If an error occurs during the API call.
    """
    device: Device = await device_dao.get_device(device_id=device_id, user_id=user.id)
    try:
        reader_api = get_reader_api(settings.mainflux_token)
        channels_api = get_channels_api(settings.mainflux_token)

        channels = channels_api.channels_get(name=tag_name).channels
        if len(channels) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        channel_id = channels[0].id

        records = reader_api.channels_chan_id_messages_get(
            chan_id=channel_id,
            publisher=str(device.mainflux_thing_uuid),
            limit=limit,
            offset=offset,
        )
        return records
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.body)
