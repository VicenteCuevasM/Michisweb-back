from uuid import UUID
from pydantic import BaseModel
from typing import List


class EntregaDetalle(BaseModel):
    id_principio: UUID
    id_lote: str              # Cambiado de UUID a str para aceptar valores como "LOTE-001"
    unidades_entregadas: int


class EntregaResponse(BaseModel):
    id_receta: UUID
    detalle: List[EntregaDetalle]
