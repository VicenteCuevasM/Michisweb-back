import os
import math
import uuid
import re

import httpx
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import Receta, PrescripcionPrincipio
from schemas import EntregaDetalle, EntregaResponse

app = FastAPI(
    title="Entrega-Service",
    description="Microservicio que calcula y descuenta unidades de medicamentos para una receta."
)

# Lee la URL base de medicamentos desde las variables de entorno
MEDICAMENTOS_BASE_URL = os.getenv("MEDICAMENTOS_BASE_URL", "http://medicamentos-service:3005")


def extraer_dias(duracion_str: str) -> int:
    """
    Extrae el número de días de un string de duración.
    Ejemplos: "5 días" -> 5, "10" -> 10.
    Si no se encuentra un entero en la cadena, lanza ValueError.
    """
    match = re.search(r"\d+", duracion_str)
    if not match:
        raise ValueError(f"No se pudo parsear la duración '{duracion_str}' a entero")
    return int(match.group(0))


@app.post(
    "/entrega/receta/{id_receta}",
    response_model=EntregaResponse,
    summary="Generar la entrega de medicamentos para una receta dada",
)
async def generar_entrega(
    id_receta: str,
    session: AsyncSession = Depends(get_session),
):
    # 1) Validar que id_receta es un UUID válido
    try:
        uuid_receta = uuid.UUID(id_receta)
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de id_receta inválido")

    # 2) Obtener la receta desde la DB
    result_rec = await session.execute(
        select(Receta).where(Receta.id_receta == uuid_receta)
    )
    receta_obj = result_rec.scalar_one_or_none()
    if receta_obj is None:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    # 3) Obtener todos los principios activos asociados a esa prescripción
    id_prescripcion = receta_obj.id_prescripcion
    result_pp = await session.execute(
        select(PrescripcionPrincipio).where(
            PrescripcionPrincipio.id_prescripcion == id_prescripcion
        )
    )
    prescrip_principios = result_pp.scalars().all()
    if not prescrip_principios:
        raise HTTPException(
            status_code=404,
            detail="No hay principios activos para la prescripción asociada a esta receta",
        )

    detalle_respuesta = []

    # 4) Crear cliente HTTP asíncrono para llamar a medicamentos-service
    async with httpx.AsyncClient(timeout=10.0) as client:
        for pp in prescrip_principios:
            id_principio = pp.id_principio
            duracion_str = pp.duracion

            # 5) Convertir duracion a un entero (días)
            try:
                dias = extraer_dias(duracion_str)
            except ValueError:
                raise HTTPException(
                    status_code=500,
                    detail=f"Formato de duración inválido para principio {id_principio}: '{duracion_str}'",
                )

            # 6) Calcular unidades = ceil(días / 2)
            unidades = math.ceil(dias / 2)

            # 7) Llamar a /medicamentos/principios/{id_principio}/proximo_vencimiento
            url_lote = f"{MEDICAMENTOS_BASE_URL}/medicamentos/principios/{id_principio}/proximo_vencimiento"
            resp_lote = await client.get(url_lote)
            if resp_lote.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"No hay lotes disponibles para el principio {id_principio}",
                )
            if resp_lote.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Error al consultar lote para principio {id_principio}",
                )

            data_lote = resp_lote.json()
            # En medicamentos-service, el campo de lote es "numero_lote" (string)
            id_lote = data_lote.get("numero_lote")
            if not id_lote:
                raise HTTPException(
                    status_code=500,
                    detail=f"Respuesta inválida de medicamentos-service para el principio {id_principio}: falta 'numero_lote'",
                )

            # 8) Llamar a /medicamentos/lotes/{id_lote}/entrega con {"cantidad": unidades}
            url_entrega = f"{MEDICAMENTOS_BASE_URL}/medicamentos/lotes/{id_lote}/entrega"
            payload = {"cantidad": unidades}
            resp_entrega = await client.post(url_entrega, json=payload)

            if resp_entrega.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Lote '{id_lote}' no encontrado al intentar descontar stock",
                )
            if resp_entrega.status_code != 200:
                detalle_error = resp_entrega.json().get("detail", "")
                raise HTTPException(
                    status_code=502,
                    detail=f"Error al descontar stock en lote '{id_lote}': {detalle_error}",
                )

            # 9) Agregar al detalle de respuesta (id_lote es cadena)
            detalle_respuesta.append(
                EntregaDetalle(
                    id_principio=id_principio,
                    id_lote=id_lote,
                    unidades_entregadas=unidades,
                )
            )

    # 10) Devolver JSON con id_receta y detalle
    return EntregaResponse(id_receta=uuid_receta, detalle=detalle_respuesta)
