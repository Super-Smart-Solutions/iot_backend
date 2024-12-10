from fastapi.routing import APIRouter

from iot_backend.web.api import (  # alerts,
    actions,
    devices,
    docs,
    echo,
    groups,
    monitoring,
    notifications,
    organizations,
    records,
    redis,
    tags,
    users,
    messages
)

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["Organizations"],
)
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])
# api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"],
)
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])
api_router.include_router(records.router, prefix="/records", tags=["Records"])
api_router.include_router(actions.router, prefix="/actions", tags=["Actions"])
api_router.include_router(messages.router, prefix="/channels", tags=["messages"])

