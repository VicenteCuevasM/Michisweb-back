from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Crea el engine asincrónico
engine = create_async_engine(DATABASE_URL, echo=True)

# Crea el session maker para sesiones asincrónicas
AsyncSessionLocal = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Dependencia para FastAPI o para uso manual
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
