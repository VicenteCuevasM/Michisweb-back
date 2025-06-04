from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from database import get_session
import crud.medicamento as crud
from schemas.medicamento import ReservarCantidad, LoteProximoVencimientoOut, ReporteDefecto, MedicamentoInfo, LoteCreateBase, LoteOut, MedicamentoOut, PrincipioActivoOut, PrincipioActivoDetalleOut, EntregaMedicamento
from crud.medicamento import reservar_medicamento, get_lote_proximo_vencimiento_info, reportar_defecto_en_lote, get_medicamento_por_codigo_barras, crear_lote_por_codigo, obtener_detalle_por_principio, obtener_todos_los_principios, entregar_medicamento

router = APIRouter(prefix="/medicamentos", tags=["Medicamentos"])

@router.get("")
async def read_medicamentos(session: AsyncSession = Depends(get_session)):
    medicamentos = await crud.get_medicamentos(session)
    # Convertimos los objetos ORM a dict para que FastAPI los pueda serializar sin schema
    return [medicamento.__dict__ for medicamento in medicamentos]

@router.get("/{id_medicamento}/lotes")
async def obtener_lotes_por_medicamento(id_medicamento: UUID, session: AsyncSession = Depends(get_session)):
    lotes = await crud.get_lotes_por_medicamento(session, id_medicamento)
    if not lotes:
        raise HTTPException(status_code=404, detail="No se encontraron lotes para este medicamento")
    return lotes

@router.get("/codigo_barras/{codigo_barras}", response_model=MedicamentoInfo)
async def obtener_info_medicamento(codigo_barras: UUID, session: AsyncSession = Depends(get_session)):
    medicamento = await get_medicamento_por_codigo_barras(session, codigo_barras)
    if not medicamento:
        raise HTTPException(status_code=404, detail="Medicamento no encontrado")
    return medicamento


@router.post("", response_model=LoteOut)
async def crear_lote(
    lote_data: LoteCreateBase,
    session: AsyncSession = Depends(get_session),
):
    return await crear_lote_por_codigo(session, lote_data)

@router.get("/principios", response_model=List[PrincipioActivoOut])
async def listar_principios(session: AsyncSession = Depends(get_session)):
    principios = await obtener_todos_los_principios(session)
    return principios

@router.get("/principios/{id_principio}", response_model=PrincipioActivoDetalleOut)
async def detalle_principio(id_principio: UUID, session: AsyncSession = Depends(get_session)):
    detalle = await obtener_detalle_por_principio(session, id_principio)
    if detalle is None:
        raise HTTPException(status_code=404, detail="Principio activo no encontrado")
    return detalle

@router.post("/lotes/{lote}/entrega")
async def registrar_entrega(lote: str, datos: EntregaMedicamento, session: AsyncSession = Depends(get_session)):
    lote_actualizado = await entregar_medicamento(session, lote, datos.cantidad)
    return lote_actualizado

@router.post("/lotes/{lote}/reportar_defecto", response_model=LoteOut)
async def reportar_defecto_lote(
    lote: str,
    data: ReporteDefecto,
    session: AsyncSession = Depends(get_session)
):
    return await reportar_defecto_en_lote(session, lote, data.tipo, data.cantidad)

@router.get("/principios/{id_principio}/proximo_vencimiento", response_model=LoteProximoVencimientoOut)
async def obtener_lote_proximo_vencimiento_con_info(
    id_principio: UUID,
    session: AsyncSession = Depends(get_session)
):
    info = await get_lote_proximo_vencimiento_info(session, id_principio)
    if info is None:
        raise HTTPException(status_code=404, detail="No hay lotes disponibles para este principio activo")
    return info

@router.post("/lotes/{lote}/reservar")
async def reservar_cantidad_lote(
    lote: str,
    entrada: ReservarCantidad,  # Pydantic model con 'cantidad: int'
    session: AsyncSession = Depends(get_session)
):
    return await reservar_medicamento(session, lote, entrada.cantidad)