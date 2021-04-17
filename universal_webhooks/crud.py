from datetime import datetime
from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from universal_webhooks import models, schemas


async def get_adapter(db: AsyncSession, id: str) -> Union[models.Adapter, None]:
    async with db.begin():
        result: models.Adapter = (
            await db.execute(select(models.Adapter).filter(models.Adapter.id == id))
        ).first()[0]
        result.last_access = datetime.now()
        return result


async def create_adapter(db: AsyncSession, adapter: schemas.AdapterCreate):
    db_adapter = models.Adapter(**adapter.dict())
    async with db.begin():
        db.add(db_adapter)
        return db_adapter


async def delete_adapter(db: AsyncSession, id: str):
    async with db.begin():
        adapter: models.Adapter = (
            await db.execute(select(models.Adapter).filter(models.Adapter.id == id))
        ).first()[0]
        db.delete(adapter)
