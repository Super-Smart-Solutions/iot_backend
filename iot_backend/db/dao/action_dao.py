from fastapi import Depends, HTTPException
from iot_backend.db.dao.base_dao import BaseDAO
from iot_backend.db.dependencies import get_db_session
from iot_backend.db.models.action import Action


class ActionDAO(BaseDAO[Action]):
    def __init__(self, session=Depends(get_db_session)):
        super().__init__(Action, session)


    async def update(self, id):
        action = await self.get_by("id", id, unique=True)
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
            # Toggle the is_enabled property
        action.is_enabled = not action.is_enabled
        await self.session.commit()
        await self.session.refresh(action)
        return action