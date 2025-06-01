from pydantic import BaseModel, EmailStr
from uuid import UUID

class PacienteBase(BaseModel):
    rut: str
    nombre: str | None = None
    numero: int | None = None
    correo: EmailStr | None = None

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(BaseModel):
    nombre: str | None = None
    numero: int | None = None
    correo: EmailStr | None = None

class PacienteOut(PacienteBase):
    id_paciente: UUID

    class Config:
        orm_mode = True
