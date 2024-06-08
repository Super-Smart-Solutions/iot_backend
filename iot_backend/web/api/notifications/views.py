from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.param_functions import Depends

from iot_backend.db.dao.alert_dao import AlertDAO
from iot_backend.db.dao.device_dao import DeviceDAO
from iot_backend.db.dao.notification_dao import NotificationDAO
from iot_backend.db.models.alert import Alert
from iot_backend.db.models.device import Device
from iot_backend.db.models.notification import Notification
from iot_backend.db.models.users import User, current_active_user

# from iot_backend.web.api.alerts.schema import NotificationDTO, NotificationInputDTO


router = APIRouter()


@router.post("/")
async def create_notification(
    request: Request,
    notification_dao: NotificationDAO = Depends(),
    device_dao: DeviceDAO = Depends(),
    alert_dao: AlertDAO = Depends(),
):
    """
    This function creates a new notification based on the request data.

    Args:
        request (Request): The request object containing the notification details.
        notification_dao (NotificationDAO, optional): The data access object for notifications. Defaults to Depends().

    Raises:
        HTTPException: If there is an error in the request, it raises an HTTPException with a 400 status code.

    Returns:
        dict: The created notification.
    """
    try:
        response = await request.json()

        device: Device = device_dao.get_by(
            field="mainflux_thing_uuid", value=response["publisher"]
        )
        alert: Alert = alert_dao.get_by(
            field="check_external_id", value=response["_check_id"]
        )

        notification = await notification_dao.create_notification(
            message=response["_message"],
            level=response["_level"],
            check_id=response["_check_id"],
            notification_endpoint_id=response["_notification_endpoint_id"],
            notification_rule_id=response["_notification_rule_id"],
            alert_id=alert.id,
            device_id=device.id,
            user_id=alert.user_id,
        )
        return notification

    except HTTPException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/")
async def get_notification(
    limit: int = 10,
    offset: int = 0,
    device_id: Optional[str] = None,
    alert_id: Optional[str] = None,
    notification_dao: NotificationDAO = Depends(),
    user: User = Depends(current_active_user),
):
    """
    This function retrieves a list of notifications.

    Args:
        limit (int, optional): The maximum number of notifications to return. Defaults to 10.
        offset (int, optional): The number of notifications to skip before starting to return. Defaults to 0.
        device_id (str, optional): The device ID to filter notifications by. Defaults to None.
        alert_id (str, optional): The alert ID to filter notifications by. Defaults to None.
        notification_dao (NotificationDAO, optional): The data access object for notifications. Defaults to Depends().

    Returns:
        list: The list of notifications.
    """
    return await notification_dao.get_all_notifications(
        limit, offset, user.id, device_id, alert_id
    )
