from sqlmodel import create_engine, SQLModel
from app.config import database_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user import User


DATABASE_URL = f"postgresql+asyncpg://{database_url}"
engine = create_async_engine(DATABASE_URL, echo=True)

# async_session = sessionmaker(
#     engine, class_=AsyncSession, expire_on_commit=False
# )


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session

        
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
