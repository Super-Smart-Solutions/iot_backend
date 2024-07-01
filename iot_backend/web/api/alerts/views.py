# from typing import Optional

# from fastapi import APIRouter, HTTPException, status
# from fastapi.param_functions import Depends
# from influxdb_client.rest import ApiException

# from iot_backend.db.dao.alert_dao import AlertDAO
# from iot_backend.db.dao.device_dao import DeviceDAO
# from iot_backend.db.models.alert import Alert
# from iot_backend.db.models.device import Device
# from iot_backend.db.models.users import User, current_active_user
# from iot_backend.services.influxdb import InfluxDBManger
# from iot_backend.web.api.alerts.schema import AlertDTO, AlertInputDTO

# router = APIRouter()
# influxdb = InfluxDBManger()


# @router.get("/")
# async def get_alerts(
#     device_id: Optional[int] = None,
#     limit: int = 10,
#     offset: int = 0,
#     alert_dao: AlertDAO = Depends(),
#     user: User = Depends(current_active_user),
# ):
#     """
#     Retrieve all Alert objects from the database.

#     :param limit: limit of alert objects, defaults to 10.
#     :param offset: offset of alert objects, defaults to 0.
#     :param alert_dao: DAO for alert models.
#     :return: list of alert objects from database.
#     """
#     return await alert_dao.get_all_alerts(
#         user_id=user.id, limit=limit, offset=offset, device_id=device_id
#     )


# @router.post("/")
# async def create_alert(
#     device_id: int,
#     new_alert_object: AlertInputDTO,
#     alert_dao: AlertDAO = Depends(),
#     device_dao: DeviceDAO = Depends(),
#     user: User = Depends(current_active_user),
# ):
#     """
#     Creates alert model in the database.

#     :param new_alert_object: new alert model item.
#     :param alert_dao: DAO for alert models.
#     """
#     device: Device = await device_dao.get_device(device_id=device_id, user_id=user.id)

#     query = influxdb.build_query(
#         node_id=device.mainflux_thing_secret,
#         channel_id="09bd29b3-70b7-4c7b-9485-9586e2cdb79e",
#     )

#     try:
#         check = influxdb.build_threshold(
#             name=new_alert_object.name,
#             comparator=new_alert_object.comparator,
#             query=query,
#             threshold=new_alert_object.threshold,
#         )
#     except ApiException as e:
#         raise HTTPException(e.status, e.message)

#     await alert_dao.create_alert_model(
#         name=new_alert_object.name,
#         comparator=new_alert_object.comparator,
#         threshold=new_alert_object.threshold,
#         status=check.status,
#         # channel_id=new_alert_object.channel_id,  ## GAP Solved
#         check_external_id=check.id,
#         check_external_message_template=check.status_message_template,
#         device_id=device.id,
#         user_id=user.id,
#     )


# @router.patch("/{alert_id}/disable")
# async def disable_alert(
#     alert_id: int,
#     alert_dao: AlertDAO = Depends(),
#     user: User = Depends(current_active_user),
# ):
#     """
#     Disable an alert.

#     Parameters:
#     - alert_id (int): The ID of the alert to disable.
#     - alert_dao (AlertDAO): The data access object for alerts.
#     - user (User): The current active user.

#     Returns:
#     - dict: A dictionary with a message indicating that the alert status was updated successfully.
#     """
#     alert: Alert = await alert_dao.get_alert(alert_id=alert_id, user_id=user.id)
#     if alert:
#         influxdb.disable_check(check_id=alert.check_external_id)

#     await alert_dao.disable_alert(alert_id=alert_id, user_id=user.id)
#     return {"message": "Alert status updated successfully"}


# @router.patch("/{alert_id}/enable")
# async def enable_alert(
#     alert_id: int,
#     alert_dao: AlertDAO = Depends(),
#     user: User = Depends(current_active_user),
# ) -> str:
#     """
#     Enable an alert.

#     Parameters:
#     - alert_id (int): The ID of the alert to enable.
#     - alert_dao (AlertDAO): The data access object for alerts.
#     - user (User): The current active user.

#     Returns:
#     - dict: A dictionary with a message indicating that the alert status was updated successfully.
#     """
#     alert: Alert = await alert_dao.get_alert(alert_id=alert_id, user_id=user.id)
#     if alert:
#         influxdb.enable_check(check_id=alert.check_external_id)

#     await alert_dao.enable_alert(alert_id=alert_id, user_id=user.id)

#     return {"message": "Alert status updated successfully"}


# @router.delete("/{alert_id}")
# async def delete_alert(
#     alert_id: int,
#     alert_dao: AlertDAO = Depends(),
#     user: User = Depends(current_active_user),
# ) -> str:
#     """
#     Delete an alert.

#     Parameters:
#     - alert_id (int): The ID of the alert to delete.
#     - alert_dao (AlertDAO): The data access object for alerts.
#     - user (User): The current active user.

#     Returns:
#     - dict: A dictionary with a message indicating that the alert was deleted successfully.
#     """
#     # Delete the check from InfluxDB
#     alert: Alert = await alert_dao.get_alert(alert_id=alert_id, user_id=user.id)
#     if alert:
#         influxdb.delete_check(check_id=alert.check_external_id)

#     # Delete the alert from the database
#     await alert_dao.delete_alert(alert_id, user_id=user.id)
#     return {"message": "Alert deleted successfully"}


# @router.patch("/disable_all_alerts")
# async def disable_all_alerts(
#     alert_dao: AlertDAO = Depends(),
#     user: User = Depends(current_active_user),
# ) -> str:
#     """
#     Disable all alerts.

#     Parameters:
#     - alert_dao (AlertDAO): The data access object for alerts.
#     - user (User): The current active user.

#     Returns:
#     - dict: A dictionary with a message indicating that all alerts were disabled successfully.
#     """
#     alerts = await alert_dao.get_by(field="status", value="enabled")
#     if not alerts:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="There are no enabled alerts to disable.",
#         )
#     for alert in alerts:
#         influxdb.disable_check(check_id=alert.check_external_id)
#         await alert_dao.disable_alert(alert.id, user_id=user.id)

#     return {"message": "All alerts disabled successfully"}
