import uvicorn

from src import app


if __name__ == "__main__":
    uvicorn.run(app=app, port=8000, host="0.0.0.0")
    