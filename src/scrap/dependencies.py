from fastapi import Depends
from fastapi.exceptions import HTTPException
from src.scrap import services
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db_session

async def valid_list_post(db:AsyncSession = Depends(get_db_session)):
    list_post = await services.get_all_post(10, db)

    if isinstance(list_post, Exception):
        raise HTTPException(
            detail=f"Error: {list_post}",
            status_code=500)

    return list_post
