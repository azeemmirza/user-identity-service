from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, instance: Any) -> None:
        self.session.add(instance)

    async def get(self, model: type[Any], entity_id: Any) -> Any | None:
        return await self.session.get(model, entity_id)

    async def scalar(self, statement: Select[Any]) -> Any | None:
        return await self.session.scalar(statement)

    async def scalars(self, statement: Select[Any]) -> Sequence[Any]:
        return (await self.session.scalars(statement)).all()

    async def delete(self, instance: Any) -> None:
        await self.session.delete(instance)

    async def flush(self) -> None:
        await self.session.flush()

    async def refresh(self, instance: Any) -> None:
        await self.session.refresh(instance)

    async def commit(self) -> None:
        await self.session.commit()

    async def connection(self) -> AsyncConnection:
        return await self.session.connection()
