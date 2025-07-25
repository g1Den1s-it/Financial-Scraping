from fastapi import FastAPI

from src.scrap import scrap
from fastapi_pagination import add_pagination

app = FastAPI()

add_pagination(app)

app.include_router(scrap)
