from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models import Base, Prescripcion, PrescripcionPrincipio, Receta
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

class PrescripcionPrincipioCreate(BaseModel):
    id_principio: uuid.UUID
    duracion: str
    frecuencia: str

class PrescripcionCreate(BaseModel):
    id_medico: uuid.UUID
    id_paciente: uuid.UUID
    principios: List[PrescripcionPrincipioCreate]

# ----------------------
# Endpoints
# ----------------------


# Crear prescripcion
@app.post("/prescripciones")
async def crear_prescripcion(
    data: PrescripcionCreate, db: AsyncSession = Depends(get_session)
):
    prescripcion = Prescripcion(
        id_medico=data.id_medico,
        id_paciente=data.id_paciente
    )
    db.add(prescripcion)
    await db.flush()

    for principio in data.principios:
        item = PrescripcionPrincipio(
            id_prescripcion=prescripcion.id_prescripcion,
            id_principio=principio.id_principio,
            duracion=principio.duracion,
            frecuencia=principio.frecuencia
        )
        db.add(item)

    await db.commit()
    return {"id_prescripcion": prescripcion.id_prescripcion}

# Obtener prescripciones de 1 paciente
@app.get("/prescripciones/paciente/{id_paciente}")
async def obtener_prescripciones(
    id_paciente: uuid.UUID, db: AsyncSession = Depends(get_session)
):
    result = await db.execute(
        select(Prescripcion)
        .options(
            selectinload(Prescripcion.principios),
            selectinload(Prescripcion.medico),
            selectinload(Prescripcion.paciente)
        )
        .where(Prescripcion.id_paciente == id_paciente)
    )
    prescripciones = result.scalars().all()

    response = []
    for p in prescripciones:
        principios = [
            {
                "id_principio": pp.id_principio,
                "duracion": pp.duracion,
                "frecuencia": pp.frecuencia
            }
            for pp in p.principios
        ]
        response.append({
            "id_prescripcion": p.id_prescripcion,
            "id_medico": p.id_medico,
            "medico_nombre": p.medico.nombre if p.medico else None,
            "id_paciente": p.id_paciente,
            "paciente_nombre": p.paciente.nombre if p.paciente else None,
            "principios": principios
        })

    return response

# Obtener 1 prescripcion
@app.get("/prescripcion/{id_prescripcion}")
async def obtener_prescripcion(
    id_prescripcion: uuid.UUID, db: AsyncSession = Depends(get_session)
):
    result = await db.execute(
        select(Prescripcion)
        .options(
            selectinload(Prescripcion.principios),
            selectinload(Prescripcion.medico),
            selectinload(Prescripcion.paciente)
        )
        .where(Prescripcion.id_prescripcion == id_prescripcion)
    )
    p = result.scalars().first()

    if not p:
        raise HTTPException(status_code=404, detail="Prescripción no encontrada")

    principios = [
        {
            "id_principio": pp.id_principio,
            "duracion": pp.duracion,
            "frecuencia": pp.frecuencia
        }
        for pp in p.principios
    ]

    return {
        "id_prescripcion": p.id_prescripcion,
        "id_medico": p.id_medico,
        "medico_nombre": p.medico.nombre if p.medico else None,
        "id_paciente": p.id_paciente,
        "paciente_nombre": p.paciente.nombre if p.paciente else None,
        "principios": principios
    }

#Obtener todas las prescripciones
@app.get("/prescripciones")
async def obtener_todas_prescripciones(db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(Prescripcion)
        .options(
            selectinload(Prescripcion.principios),
            selectinload(Prescripcion.medico),
            selectinload(Prescripcion.paciente)
        )
    )
    prescripciones = result.scalars().all()

    response = []
    for p in prescripciones:
        principios = [
            {
                "id_principio": pp.id_principio,
                "duracion": pp.duracion,
                "frecuencia": pp.frecuencia
            }
            for pp in p.principios
        ]
        response.append({
            "id_prescripcion": p.id_prescripcion,
            "id_medico": p.id_medico,
            "medico_nombre": p.medico.nombre if p.medico else None,
            "id_paciente": p.id_paciente,
            "paciente_nombre": p.paciente.nombre if p.paciente else None,
            "principios": principios
        })

    return response

# Agregar 1 receta de la prescripcion
@app.post("/prescripciones/agregar-receta/{id_prescripcion}")
async def agregar_receta(id_prescripcion: uuid.UUID, db: AsyncSession = Depends(get_session)):
    # Buscar prescripción
    result = await db.execute(
        select(Prescripcion).where(Prescripcion.id_prescripcion == id_prescripcion)
    )
    prescripcion = result.scalar_one_or_none()

    if not prescripcion:
        raise HTTPException(status_code=404, detail="Prescripción no encontrada")

    receta = Receta(
        id_prescripcion=prescripcion.id_prescripcion,
        id_paciente=prescripcion.id_paciente,
        id_medico=prescripcion.id_medico,
        fecha_emision=datetime.now(timezone.UTC),
        estado="pendiente"
    )
    db.add(receta)
    await db.commit()
    return {"mensaje": "Receta creada correctamente", "id_receta": receta.id_receta}


# Obtener todas las recetas
@app.get("/recetas")
async def obtener_recetas(db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(Receta)
        .options(
          selectinload(Receta.medico),
          selectinload(Receta.paciente)
        )
    )
    recetas = result.scalars().all()

    return [
        {
            "id_receta": r.id_receta,
            "id_prescripcion": r.id_prescripcion,
            "id_paciente": r.id_paciente,
            "nombre_paciente": r.paciente.nombre,
            "id_medico": r.id_medico,
            "nombre_medico": r.medico.nombre,
            "fecha_emision": r.fecha_emision,
            "estado": r.estado
        } for r in recetas
    ]

# Obtener 1 receta
@app.get("/recetas/{id_receta}")
async def obtener_receta(id_receta: uuid.UUID, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(Receta)
        .where(Receta.id_receta == id_receta)
        .options(
          selectinload(Receta.medico),
          selectinload(Receta.paciente)
        )
    )
    r = result.scalar_one_or_none()

    if not r:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    return {
            "id_receta": r.id_receta,
            "id_prescripcion": r.id_prescripcion,
            "id_paciente": r.id_paciente,
            "nombre_paciente": r.paciente.nombre,
            "id_medico": r.id_medico,
            "nombre_medico": r.medico.nombre,
            "fecha_emision": r.fecha_emision,
            "estado": r.estado
        }

