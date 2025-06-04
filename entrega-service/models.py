# entrega-service/models.py

import uuid
from sqlalchemy import Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Receta(Base):
    __tablename__ = "receta"

    id_receta = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    id_prescripcion = Column(
        UUID(as_uuid=True), ForeignKey("prescripcion.id_prescripcion"), nullable=False
    )
    # Nota: solo necesitamos id_prescripcion para nuestro flujo,
    # el resto de campos (paciente, médico, fecha_emision, estado) se omiten.


class PrescripcionPrincipio(Base):
    __tablename__ = "prescripcion_principio"

    id_prescripcion = Column(
        UUID(as_uuid=True),
        ForeignKey("prescripcion.id_prescripcion"),
        primary_key=True,
    )
    id_principio = Column(
        UUID(as_uuid=True), ForeignKey("principio_activo.id_principio"), primary_key=True
    )
    duracion = Column(String(100), nullable=False)
    # Aquí duracion se almacena como texto (p. ej. "5", "5 días", etc.),
    # pero en main.py extraeremos el número entero para el cálculo.
