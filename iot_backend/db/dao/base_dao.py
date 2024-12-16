from typing import Any, Generic, TypeVar, List, Optional, Union

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from iot_backend.db.base import Base
from iot_backend.db.dependencies import get_db_session

ModelType = TypeVar("ModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class BaseDAO(Generic[ModelType]):
    """
    Base Data Access Object (DAO) for interacting with database models.

    Provides common CRUD operations for SQLAlchemy models using Pydantic schemas
    for data serialization and validation.

    Args:
        model (ModelType): The SQLAlchemy model class to interact with.
        session (AsyncSession, optional): An asynchronous SQLAlchemy session.
                                         Defaults to Depends(get_db_session).

    Attributes:
        model (ModelType): The SQLAlchemy model class.
        session (AsyncSession): The SQLAlchemy session.

    Example Usage:

        # Assuming 'User' is your SQLAlchemy model and 'UserSchema' is your Pydantic schema
        class UserDAO(BaseDAO[User, UserSchema]):
            def __init__(self, session: AsyncSession = Depends(get_db_session)):
                super().__init__(User, session)

        # Create an instance of the DAO
        user_dao = UserDAO()

        # Create a new user
        new_user = await user_dao.create(schema=UserSchema(username="testuser", email="test@example.com"))

    """

    def __init__(
        self, model: ModelType, session: AsyncSession = Depends(get_db_session)
    ):
        self.model = model
        self.session = session

    async def get(self, id: int) -> Optional[ModelType]:
        """
        Retrieve a model instance by its ID.

        Args:
            id (int): The ID of the model instance.

        Returns:
            Optional[ModelType]: The model instance if found, otherwise None.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().one_or_none()

    async def get_by(
        self,
        field: str,
        value: Any,
        unique: bool = False,
    ) -> Union[Optional[ModelType], List[ModelType]]:
        """Retrieves records based on a field and value.

        Args:
            field (str): The name of the field to filter by.
            value (Any): The value to filter for.
            unique (bool): Whether to return a single record or all matching records. Defaults to False.

        Returns:
            Union[Optional[ModelType], List[ModelType]]: The retrieved record(s) or None if not found.
        """  # noqa: E501
        query = select(self.model).filter(
            getattr(self.model, field) == value,
        )

        result = await self.session.execute(query)
        if unique:
            return result.scalars().first()
        return list(result.scalars().all())

    async def create(self, schema: SchemaType) -> ModelType:
        """
        Create a new model instance.

        Args:
            schema (SchemaType): The Pydantic schema representing the data.

        Returns:
            ModelType: The created model instance.
        """
        instance = self.model(**schema.model_dump())
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: int, schema: SchemaType) -> Optional[ModelType]:
        """
        Update an existing model instance.

        Args:
            id (int): The ID of the model instance to update.
            schema (SchemaType): The Pydantic schema with updated data.

        Returns:
            Optional[ModelType]: The updated model instance if found, otherwise None.
        """
        instance = await self.get(id)
        if instance:
            for key, value in schema.model_dump(exclude_unset=True).items():
                setattr(instance, key, value)
            await self.session.commit()
            await self.session.refresh(instance)
        return instance

    async def delete(self, id: int) -> Optional[ModelType]:
        """
        Delete a model instance.

        Args:
            id (int): The ID of the model instance to delete.

        Returns:
            Optional[ModelType]: The deleted model instance if found, otherwise None.
        """
        instance = await self.get(id)
        if instance:
            await self.session.delete(instance)
            await self.session.commit()
        return instance

    async def list(self, limit: int = 10, offset: int = 0) -> List[ModelType]:
        """
        Retrieve a list of model instances with pagination.

        Args:
            limit (int, optional): The maximum number of instances to retrieve. Defaults to 10.
            offset (int, optional): The offset for pagination. Defaults to 0.

        Returns:
            List[ModelType]: A list of model instances.
        """
        result = await self.session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())
