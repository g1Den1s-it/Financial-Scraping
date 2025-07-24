import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine, AsyncConnection
from sqlalchemy.orm import declarative_base


load_dotenv()

SQL_DATABASE_URL = (f"postgresql+asyncpg://"
                    f"{os.getenv('DB_USER')}:"
                    f"{os.getenv('DB_PASSWORD')}@"
                    f"{os.getenv('DB_HOST')}:"
                    f"{os.getenv('DB_PORT')}/"
                    f"{os.getenv('DB_NAME')}")


class AsyncDatabaseSessionManager:
    def __init__(self, sql_url):
        self._engine = create_async_engine(sql_url, future=True, echo=True)
        self._session = async_sessionmaker(
            self._engine, expire_on_commit=False, class_= AsyncSession
        )


    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        async with self._engine.begin() as conn:
            try:
                yield conn
            except Exception as e:
                await conn.rollback()
                raise e


    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if not self._session or not self._engine:
            raise Exception("AsyncDataSessionManager is not initialized!")

        session: AsyncSession = self._session()

        try:
            yield session
        except Exception:
            await session.rollback()
            await session.close()
            raise
        finally:
            await session.close()


async_session_manager = AsyncDatabaseSessionManager(SQL_DATABASE_URL)

Base = declarative_base()

async def get_db_session():
    async with async_session_manager.session() as session:
        yield session
