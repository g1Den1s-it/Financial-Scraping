from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate 
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db_session
from src.scrap.schemas import PostSchema

from src.scrap.dependencies import valid_list_post, valid_all_post_query

scrap = APIRouter(prefix="/financial")



@scrap.get("/post-list",
    response_model=Page[PostSchema],
    status_code=200
)
async def get_list_post(query = Depends(valid_all_post_query), db: AsyncSession = Depends(get_db_session)):
    return await sqlalchemy_paginate(db, query)
 