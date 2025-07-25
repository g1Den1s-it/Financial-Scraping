from fastapi import APIRouter, Depends

from src.scrap.schemas import PostSchema

from src.scrap.dependencies import valid_list_post

scrap = APIRouter(prefix="/financial")



@scrap.get("/post-list/",
    response_model=list[PostSchema],
    status_code=200
)
async def get_list_post(list_post: list[PostSchema] = Depends(valid_list_post)):
    return list_post
