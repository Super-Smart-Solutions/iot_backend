from uuid import UUID
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from iot_backend.db.dao.base_dao import BaseDAO
from iot_backend.db.dependencies import get_db_session
from iot_backend.db.models.message import Message


class MessageDAO(BaseDAO[Message]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        super().__init__(Message, session)


    async def create(self, tag_id: int, device_id: int, user_id: UUID, schema):
        record_data = schema.model_dump()
        record_data["tag_id"] = tag_id
        record_data["device_id"] = device_id
        record_data["user_id"] = user_id
        instance = self.model(**record_data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance