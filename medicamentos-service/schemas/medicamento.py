from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List
from enum import Enum

class MedicamentoInfo(BaseModel):
    nombre: str
    dosis_concentracion: str
    via_administracion: str

    class Config:
        orm_mode = True

class LoteCreateBase(BaseModel):
    codigo_barras: UUID
    lote: str
    fecha_vencimiento: datetime
    cantidad: int
    hay_defectuosos: bool = False  # <- checkbox del usuario
    cantidad_reservada: int

    # estos campos se incluirán solo si hay defectuosos
    cantidad_defectuosa: int | None = None
    cantidad_en_idea: int | None = None
    cantidad_en_estado: int | None = None
    cantidad_envase_roto: int | None = None


class LoteOut(BaseModel):
    id_lote: UUID
    lote: str
    fecha_vencimiento: datetime
    cantidad: int
    cantidad_defectuosa: int
    cantidad_en_idea: int
    cantidad_en_estado: int
    cantidad_envase_roto: int
    id_medicamento: UUID

    class Config:
        orm_mode = True

class MedicamentoOut(BaseModel):
    id_medicamento: UUID
    nombre: str
    dosis_concentracion: str
    via_administracion: str

    class Config:
        orm_mode = True
        
class PrincipioActivoOut(BaseModel):
    id_principio: UUID
    nombre: str
    categoria: str

    class Config:
        orm_mode = True

class MedicamentoCantidadOut(BaseModel):
    id_medicamento: UUID
    nombre: str
    dosis_concentracion: str
    via_administracion: str
    cantidad_total: int

    class Config:
        orm_mode = True

class PrincipioActivoDetalleOut(BaseModel):
    id_principio: UUID
    nombre: str
    categoria: str
    cantidad_total_medicamentos: int
    medicamentos_diferentes: int
    medicamentos: List[MedicamentoCantidadOut]

    class Config:
        orm_mode = True

class EntregaMedicamento(BaseModel):
    cantidad: int = Field(..., gt=0, description="Cantidad a entregar (debe ser > 0)")

class TipoDefecto(str, Enum):
    defectuoso = "defectuoso"
    vencido = "vencido"
    mal_estado = "mal_estado"
    envase_roto = "envase_roto"

class ReporteDefecto(BaseModel):
    tipo: TipoDefecto
    cantidad: int

class LoteProximoVencimientoOut(BaseModel):
    nombre_principio: str
    nombre_medicamento: str
    via_administracion: str
    dosis_concentracion: str
    numero_lote: str

    class Config:
        orm_mode = True

class ReservarCantidad(BaseModel):
    cantidad: int