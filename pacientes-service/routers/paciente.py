from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from database import get_session
from schemas import PacienteCreate, PacienteUpdate, PacienteOut
import crud.paciente as crud

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

@router.get("/", response_model=list[PacienteOut])
async def read_pacientes(session: AsyncSession = Depends(get_session)):
    return await crud.get_pacientes(session)

@router.get("/{paciente_id}", response_model=PacienteOut)
async def read_paciente(paciente_id: UUID, session: AsyncSession = Depends(get_session)):
    db_paciente = await crud.get_paciente(session, paciente_id)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return db_paciente

@router.post("/", response_model=PacienteOut)
async def create_paciente(paciente: PacienteCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_paciente(session, paciente)

@router.put("/{paciente_id}", response_model=PacienteOut)
async def update_paciente(paciente_id: UUID, paciente: PacienteUpdate, session: AsyncSession = Depends(get_session)):
    db_paciente = await crud.update_paciente(session, paciente_id, paciente)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return db_paciente