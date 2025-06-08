from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from uuid import UUID
from typing import List
from datetime import datetime, timezone

from models import (
    Medicamento,
    MedicamentoLote,
    PrincipioActivo,
    MedicamentoPrincipio,
    Receta,
    PrescripcionPrincipio,
    Entrega
)
from schemas.medicamento import LoteCreateBase  # si ya lo necesitas abajo

async def get_medicamentos(db: AsyncSession):
    result = await db.execute(select(Medicamento))
    return result.scalars().all()

async def get_lotes_por_medicamento(session: AsyncSession, id_medicamento: UUID):
    result = await session.execute(
        select(MedicamentoLote).where(MedicamentoLote.id_medicamento == id_medicamento)
    )
    return result.scalars().all()

async def get_medicamento_por_codigo_barras(session: AsyncSession, codigo_barras: UUID):
    result = await session.execute(
        select(Medicamento).where(Medicamento.codigo_barras == codigo_barras)
    )
    return result.scalars().first()

async def crear_lote_por_codigo(session: AsyncSession, data: LoteCreateBase):
    # Buscar el medicamento por código de barras
    result = await session.execute(
        select(Medicamento).where(Medicamento.codigo_barras == data.codigo_barras)
    )
    medicamento = result.scalar_one_or_none()
    data.cantidad_reservada = 0

    # Si no hay defectuosos, inicializamos todos esos campos en 0
    if not data.hay_defectuosos:
        data.cantidad_defectuosa = 0
        data.cantidad_en_idea = 0
        data.cantidad_en_estado = 0
        data.cantidad_envase_roto = 0

    lote = MedicamentoLote(
        id_medicamento=medicamento.id_medicamento,
        lote=data.lote,
        fecha_vencimiento=data.fecha_vencimiento,
        cantidad=data.cantidad,
        cantidad_defectuosa=data.cantidad_defectuosa,
        cantidad_en_idea=data.cantidad_en_idea,
        cantidad_en_estado=data.cantidad_en_estado,
        cantidad_envase_roto=data.cantidad_envase_roto,
    )

    session.add(lote)
    await session.commit()
    await session.refresh(lote)

    return lote

async def obtener_todos_los_principios(session: AsyncSession):
    result = await session.execute(select(PrincipioActivo))
    return result.scalars().all()

async def obtener_detalle_por_principio(session: AsyncSession, id_principio: UUID):
    result = await session.execute(
        select(PrincipioActivo)
        .where(PrincipioActivo.id_principio == id_principio)
        .options(selectinload(PrincipioActivo.medicamentos).selectinload(Medicamento.lotes))
    )
    principio = result.scalar_one_or_none()
    if principio is None:
        return None

    medicamentos = []
    total_cantidad = 0

    for medicamento in principio.medicamentos:
        cantidad_medicamento = sum(lote.cantidad for lote in medicamento.lotes if lote.cantidad is not None)
        total_cantidad += cantidad_medicamento
        medicamentos.append({
            "id_medicamento": medicamento.id_medicamento,
            "nombre": medicamento.nombre,
            "dosis_concentracion": medicamento.dosis_concentracion,
            "via_administracion": medicamento.via_administracion,
            "cantidad_total": cantidad_medicamento
        })

    return {
        "id_principio": principio.id_principio,
        "nombre": principio.nombre,
        "categoria": principio.categoria,
        "cantidad_total_medicamentos": total_cantidad,
        "medicamentos_diferentes": len(principio.medicamentos),
        "medicamentos": medicamentos
    }

async def entregar_medicamento(session: AsyncSession, lote: str, cantidad: int):
    result = await session.execute(select(MedicamentoLote).where(MedicamentoLote.lote == lote))
    lote_obj = result.scalar_one_or_none()

    if lote_obj is None:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    if lote_obj.cantidad < cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente para realizar la entrega")

    lote_obj.cantidad -= cantidad
    await session.commit()
    await session.refresh(lote_obj)
    return lote_obj

async def reportar_defecto_en_lote(session: AsyncSession, lote: str, tipo: str, cantidad: int):
    result = await session.execute(
        select(MedicamentoLote).where(MedicamentoLote.lote == lote)
    )
    lote_obj = result.scalar_one_or_none()
    
    if lote_obj is None:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    if tipo == "defectuoso":
        lote_obj.cantidad_defectuosa += cantidad
    elif tipo == "vencido":
        lote_obj.cantidad_en_estado += cantidad  # si este campo es el correcto para vencido
    elif tipo == "mal_estado":
        lote_obj.cantidad_en_idea += cantidad  # si este campo representa "mal estado"
    elif tipo == "envase_roto":
        lote_obj.cantidad_envase_roto += cantidad
    else:
        raise HTTPException(status_code=400, detail="Tipo de defecto no válido")

    await session.commit()
    await session.refresh(lote_obj)
    return lote_obj

async def get_lote_proximo_vencimiento_info(session: AsyncSession, id_principio: UUID):
    stmt = (
        select(MedicamentoLote, Medicamento, PrincipioActivo)
        .join(Medicamento, Medicamento.id_medicamento == MedicamentoLote.id_medicamento)
        .join(MedicamentoPrincipio, MedicamentoPrincipio.id_medicamento == Medicamento.id_medicamento)
        .join(PrincipioActivo, PrincipioActivo.id_principio == MedicamentoPrincipio.id_principio)
        .where(
            MedicamentoPrincipio.id_principio == id_principio,
            MedicamentoLote.cantidad > 0
        )
        .order_by(MedicamentoLote.fecha_vencimiento.asc())
        .limit(1)
    )

    result = await session.execute(stmt)
    row = result.first()

    if not row:
        return None

    lote, medicamento, principio = row

    return {
        "nombre_principio": principio.nombre,
        "nombre_medicamento": medicamento.nombre,
        "via_administracion": medicamento.via_administracion,
        "dosis_concentracion": medicamento.dosis_concentracion,
        "numero_lote": lote.lote,
    }

async def reservar_medicamento(session, lote: str, cantidad: int):
    result = await session.execute(
        select(MedicamentoLote).where(MedicamentoLote.lote == lote)
    )
    lote_obj = result.scalar_one_or_none()

    if lote_obj is None:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    if lote_obj.cantidad < cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente para realizar la reserva")

    lote_obj.cantidad_reservada += cantidad
    await session.commit()
    await session.refresh(lote_obj)
    return lote_obj

# ---------------------------------------------------------
# Nueva lógica de entrega por receta
# ---------------------------------------------------------
async def procesar_entrega_receta(
    session: AsyncSession,
    id_receta: UUID,
    id_funcionario: UUID,
    rut_retiro: str,
    nombre_retiro: str
) -> List[dict]:
    # 1. Obtener la receta
    result = await session.execute(
        select(Receta).where(Receta.id_receta == id_receta)
    )
    receta = result.scalar_one_or_none()
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    # 2. Obtener los principios de la prescripción asociada
    result = await session.execute(
        select(PrescripcionPrincipio)
        .where(PrescripcionPrincipio.id_prescripcion == receta.id_prescripcion)
    )
    principios = result.scalars().all()

    respuestas: List[dict] = []

    # 3. Para cada principio, calcular unidades y procesar entrega
    for pp in principios:
        # Parseo de "X días"
        try:
            dias = int(pp.duracion.split()[0])
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"Formato de duración inválido en principio {pp.id_principio}: {pp.duracion}"
            )
        unidades = dias // 2

        # Obtener nombre de principio para la respuesta
        res_princ = await session.execute(
            select(PrincipioActivo).where(PrincipioActivo.id_principio == pp.id_principio)
        )
        princ_obj = res_princ.scalar_one_or_none()
        nombre_princ = princ_obj.nombre if princ_obj else ""

        if unidades <= 0:
            respuestas.append({
                "id_principio": pp.id_principio,
                "nombre_principio": nombre_princ,
                "cantidad_solicitada": unidades,
                "cantidad_entregada": 0,
                "estado": "sin_stock"
            })
            continue

        # Buscar lote óptimo
        info = await get_lote_proximo_vencimiento_info(session, pp.id_principio)
        if not info:
            respuestas.append({
                "id_principio": pp.id_principio,
                "nombre_principio": nombre_princ,
                "cantidad_solicitada": unidades,
                "cantidad_entregada": 0,
                "estado": "sin_stock"
            })
            continue

        # Descontar stock
        lote_num = info["numero_lote"]
        lote_actualizado = await entregar_medicamento(session, lote_num, unidades)

        respuestas.append({
            "id_principio": pp.id_principio,
            "nombre_principio": info["nombre_principio"],
            "nombre_medicamento": info["nombre_medicamento"],
            "numero_lote": lote_num,
            "cantidad_solicitada": unidades,
            "cantidad_entregada": unidades,
            "estado": "entregado"
        })

    # 4. Registrar la entrega en la tabla Entrega
    entrega = Entrega(
        id_receta=id_receta,
        id_funcionario=id_funcionario,
        fecha=datetime.now(timezone.utc),
        estado="entregado",
        rut_retiro=rut_retiro,
        nombre_retiro=nombre_retiro
    )
    session.add(entrega)
    await session.commit()

    return respuestas
