from fastapi import FastAPI

from src.scrap import scrap

app = FastAPI()


app.include_router(scrap)
