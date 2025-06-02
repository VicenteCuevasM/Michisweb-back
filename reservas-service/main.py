from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models import Base, Reserva, ReservaMedicamento
from database import engine, get_session
from pydantic import BaseModel
from typing import List
from datetime import datetime, timezone
import uuid

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ----------------------
# Pydantic Schemas
# ----------------------

class ReservaMedicamentoCreate(BaseModel):
    id_medicamento: uuid.UUID
    cantidad: int

class ReservaCreate(BaseModel):
    id_paciente: uuid.UUID
    fecha: datetime
    estado: str
    medicamentos: List[ReservaMedicamentoCreate]

# ----------------------
# Endpoints
# ----------------------

# Crear 1 reserva
@app.post("/reservas")
async def crear_reserva(data: ReservaCreate, db: AsyncSession = Depends(get_session)):
    reserva = Reserva(id_paciente = data.id_paciente,
                      fecha = data.fecha,
                      estado = data.estado) #Por defecto, al crear una reserva el estado debería ser "No confirmado"
    db.add(reserva)
    await db.flush() #Esto genera id_reserva automáticamente
    for reserva_medicamento in data.medicamentos:
        item = ReservaMedicamento(id_reserva = reserva.id_reserva,
                                  id_medicamento = reserva_medicamento.id_medicamento,
                                  cantidad = reserva_medicamento.cantidad)
        db.add(item)
    await db.commit()
    return {"id_reserva": reserva.id_reserva}

# Obtener todas las reservas, ordenadas por fecha, de la más antigua a la más reciente
@app.get("/reservas")
async def obtener_reservas(db: AsyncSession = Depends(get_session)):
    resultado = await db.execute(select(Reserva).options(selectinload(Reserva.medicamentos)).order_by(asc(Reserva.fecha)))
    reservas = resultado.scalars().all()
    return [
        {
            "id_reserva": r.id_reserva,
            "id_paciente": r.id_paciente,
            "fecha": r.fecha,
            "estado": r.estado,
            "medicamentos": [
                {
                    "id_medicamento": rm.id_medicamento,
                    "cantidad": rm.cantidad
                } for rm in r.medicamentos
            ]
        } for r in reservas
    ]

# Confirmar 1 reserva
@app.put("/reservas/{id_reserva}")
async def confirmar_reserva(id_reserva: uuid.UUID,
                            db: AsyncSession = Depends(get_session)):
    resultado = await db.execute(select(Reserva).where(Reserva.id_reserva == id_reserva))
    reserva = resultado.scalar_one_or_none()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    reserva.estado = "Confirmado"
    await db.commit()
    await db.refresh(reserva)
    return reserva