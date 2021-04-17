import logging
from typing import List

import aiohttp
import pyjq
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi_utils.tasks import repeat_every
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import func, select

from universal_webhooks import crud, database, schemas, settings
from universal_webhooks.models import Adapter

log = logging.getLogger(__name__)

app = FastAPI()


if settings.settings.debug:
    import debugpy

    debugpy.listen(("0.0.0.0", 5678))
    log.debug("debugpy listening on 0.0.0.0:5678")
    debugpy.wait_for_client()
    log.debug("debugpy waiting for client")


async def get_db_session() -> AsyncSession:
    async with database.SessionLocal() as session:
        yield session


MAX_ADAPTERS = 2


@app.on_event("startup")
@repeat_every(seconds=settings.settings.clean_interval)
async def remove_old_adapters() -> None:
    try:
        async with database.SessionLocal() as session:
            session: AsyncSession = session  # type: ignore
            async with session.begin():
                query = select([func.count()]).select_from(Adapter)
                count: int = (await session.execute(query)).first()[0]
                if count > MAX_ADAPTERS:
                    query = (
                        select(Adapter)
                        .order_by(Adapter.last_access.desc())
                        .limit(count - MAX_ADAPTERS)
                    )
                    results: List[Adapter] = (await session.execute(query)).all()
                    for result in results:
                        await session.delete(result[0])
                    await session.commit()

    except Exception as e:
        print(e)


@app.post("/webhook/", response_model=schemas.Adapter)
async def create_adapter(
    adapter: schemas.AdapterCreate, db: AsyncSession = Depends(get_db_session)
):
    new_adapter = await crud.create_adapter(db, adapter=adapter)
    return new_adapter


@app.post("/webhook/{webhook_id}")
async def execute_webhook(
    webhook_id: str, request: Request, db: AsyncSession = Depends(get_db_session)
):
    adapter = await crud.get_adapter(db, id=webhook_id)
    if adapter is None:
        raise HTTPException(status_code=404, detail="Adapter not found")
    original_payload = await request.json()
    new_payload = pyjq.first(adapter.translation_query, original_payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(adapter.send_to, json=new_payload) as response:
            print(response.status)
            response_text = await response.text()
            print(response_text)
            return response_text
