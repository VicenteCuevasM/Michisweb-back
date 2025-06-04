# entrega-service/database.py

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Leemos la URL de la base de datos desde .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Creamos el engine asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Configuramos el sessionmaker para sesiones asíncronas
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """
    Dependency de FastAPI para inyectar una sesión asíncrona.
    """
    async with AsyncSessionLocal() as session:
        yield session
