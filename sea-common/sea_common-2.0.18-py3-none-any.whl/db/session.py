from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession

from ..config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
async_engine: AsyncEngine = create_async_engine(settings.ASYNC_SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
