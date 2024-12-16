from fastapi import APIRouter, Depends, HTTPException, status
from iot_backend.db.dao.device_dao import DeviceDAO
from iot_backend.db.models.users import User, current_active_user
from iot_backend.web.api.actions.schema import ActionCreate, ActionRead
from iot_backend.db.dao.action_dao import ActionDAO

router = APIRouter()


@router.post("/", response_model=ActionRead, status_code=status.HTTP_201_CREATED)
async def create_action(
    action_data: ActionCreate,
    action_dao: ActionDAO = Depends(),
    device_dao: DeviceDAO = Depends(),
    user: User = Depends(current_active_user),
):
    await device_dao.get_device(action_data.device_id, user.id)
    return await action_dao.create(action_data)


@router.get(
    "/{action_id}",
    response_model=ActionRead,
    dependencies=[Depends(current_active_user)],
)
async def get_action(action_id: int, action_dao: ActionDAO = Depends()):
    action = await action_dao.get(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


@router.patch(
    "/{action_id}/toggle",
    response_model=ActionRead,
    dependencies=[Depends(current_active_user)],
)
async def update_action(action_id: int, action_dao: ActionDAO = Depends()):
    """Toggle the is_enabled property of an action."""

    return await action_dao.update(action_id)


@router.delete(
    "/{action_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(current_active_user)],
)
async def delete_action(action_id: int, action_dao: ActionDAO = Depends()):
    deleted_action = await action_dao.delete(action_id)
    if not deleted_action:
        raise HTTPException(status_code=404, detail="Action not found")


