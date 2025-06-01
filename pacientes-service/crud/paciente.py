from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from models import Paciente
from schemas import PacienteCreate, PacienteUpdate

async def get_pacientes(db: AsyncSession):
    result = await db.execute(select(Paciente))
    return result.scalars().all()

async def get_paciente(db: AsyncSession, paciente_id: UUID):
    result = await db.execute(select(Paciente).where(Paciente.id_paciente == paciente_id))
    return result.scalars().first()

async def create_paciente(db: AsyncSession, paciente: PacienteCreate):
    db_paciente = Paciente(**paciente.dict())
    db.add(db_paciente)
    await db.commit()
    await db.refresh(db_paciente)
    return db_paciente

async def update_paciente(db: AsyncSession, paciente_id: UUID, paciente: PacienteUpdate):
    db_paciente = await get_paciente(db, paciente_id)
    if db_paciente:
        for key, value in paciente.dict(exclude_unset=True).items():
            setattr(db_paciente, key, value)
        await db.commit()
        await db.refresh(db_paciente)
    return db_paciente
