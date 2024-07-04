from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends
from mainflux_client.models.sen_ml_record import SenMLRecord
from mainflux_client.rest import ApiException

from iot_backend.db.dao.device_dao import DeviceDAO
from iot_backend.db.models.device import Device
from iot_backend.db.models.users import User, current_active_user
from iot_backend.services.mainflux import get_channel_id, get_messages_api

router = APIRouter()


@router.post(
    "/",
    dependencies=[Depends(current_active_user)], status_code=status.HTTP_201_CREATED,
)
async def send(
    device_id: int,
    value: int,
    user: User = Depends(current_active_user),
    device_dao: DeviceDAO = Depends(),
) -> str:
    """
    Sends messages to a channel.

    Args:
        device_id (int): ID of the device (required).
        value (int): Value parameter that accepts only 0 or 1 (required).

    Raises:
        HTTPException: If an error occurs during the API call.
    """
    if value not in [0, 1]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid value. Only 0 or 1 is allowed.",
        )

    device: Device = await device_dao.get_device(device_id=device_id, user_id=user.id)
    try:
        # channels_api = get_channels_api(settings.mainflux_token)
        # channels = channels_api.channels_get(name=tag_name).channels
        # if len(channels) == 0:
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        # channel_id = channels[0].id

        channel_id = get_channel_id(uuid=str(device.mainflux_thing_uuid))
        messages_dependency = get_messages_api(
            thing_secret=str(device.mainflux_thing_secret)
        )
        messages_dependency.channels_id_messages_post(
            channel_id,
            sen_ml_record=[
                SenMLRecord(
                    bn=f"{device.mainflux_thing_uuid}", n="PUMP", u="toggle", v=value
                )
            ],
        )
        return {"message": "Sent Successfully"}
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.body)
