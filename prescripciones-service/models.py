from sqlalchemy import Column, String, ForeignKey, text, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    rut = Column(String(20), nullable=False)
    nombre = Column(String(100))
    contrasena = Column(String(100))
    rol = Column(String(50), nullable=False)

    prescripciones = relationship("Prescripcion", back_populates="medico", foreign_keys="Prescripcion.id_medico")


class Turno(Base):
    __tablename__ = "turno"

    id_turno = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    nombre = Column(String(100))
    fecha_inicio = Column(TIMESTAMP)
    fecha_fin = Column(TIMESTAMP)


class Box(Base):
    __tablename__ = "box"

    id_box = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    nombre = Column(String(100))
    piso = Column(Integer)


class Asistencia(Base):
    __tablename__ = "asistencia"

    id_asistencia = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    id_medico = Column(UUID(as_uuid=True), ForeignKey("usuario.id"))
    id_turno = Column(UUID(as_uuid=True), ForeignKey("turno.id_turno"))
    id_box = Column(UUID(as_uuid=True), ForeignKey("box.id_box"))


class Paciente(Base):
    __tablename__ = "paciente"

    id_paciente = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    rut = Column(String(20), nullable=False)
    nombre = Column(String(100))
    numero = Column(Integer)
    correo = Column(String(100))

    prescripciones = relationship("Prescripcion", back_populates="paciente", foreign_keys="Prescripcion.id_paciente")


class PrincipioActivo(Base):
    __tablename__ = "principio_activo"

    id_principio = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    nombre = Column(String(100))
    categoria = Column(String(100))


class Medicamento(Base):
    __tablename__ = "medicamento"

    id_medicamento = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    nombre = Column(String(100))


class MedicamentoPrincipio(Base):
    __tablename__ = "medicamento_principio"

    id_medicamento = Column(UUID(as_uuid=True), ForeignKey("medicamento.id_medicamento"), primary_key=True)
    id_principio = Column(UUID(as_uuid=True), ForeignKey("principio_activo.id_principio"), primary_key=True)


class MedicamentoLote(Base):
    __tablename__ = "medicamento_lote"

    codigo_barras = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    id_medicamento = Column(UUID(as_uuid=True), ForeignKey("medicamento.id_medicamento"))
    lote = Column(String(50))
    fecha_vencimiento = Column(TIMESTAMP)
    cantidad = Column(Integer)
    cantidad_defectuosa = Column(Integer)
    cantidad_en_idea = Column(Integer)
    cantidad_en_estado = Column(Integer)
    cantidad_envase_roto = Column(Integer)
    dosis_concentracion = Column(String(100))
    via_administracion = Column(String(100))


class Prescripcion(Base):
    __tablename__ = "prescripcion"

    id_prescripcion = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    id_medico = Column(UUID(as_uuid=True), ForeignKey("usuario.id"))
    id_paciente = Column(UUID(as_uuid=True), ForeignKey("paciente.id_paciente"))

    principios = relationship("PrescripcionPrincipio", back_populates="prescripcion")

    medico = relationship("Usuario", back_populates="prescripciones", foreign_keys=[id_medico])
    paciente = relationship("Paciente", back_populates="prescripciones", foreign_keys=[id_paciente])


class PrescripcionPrincipio(Base):
    __tablename__ = "prescripcion_principio"

    id_prescripcion = Column(UUID(as_uuid=True), ForeignKey("prescripcion.id_prescripcion"), primary_key=True)
    id_principio = Column(UUID(as_uuid=True), ForeignKey("principio_activo.id_principio"), primary_key=True)
    duracion = Column(String(100))
    frecuencia = Column(String(100))

    prescripcion = relationship("Prescripcion", back_populates="principios")


class Receta(Base):
    __tablename__ = "receta"

    id_receta = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    id_prescripcion = Column(UUID(as_uuid=True), ForeignKey("prescripcion.id_prescripcion"))
    id_paciente = Column(UUID(as_uuid=True), ForeignKey("paciente.id_paciente"))
    id_medico = Column(UUID(as_uuid=True), ForeignKey("usuario.id"))
    fecha_emision = Column(TIMESTAMP)
    estado = Column(String(50))

    medico = relationship("Usuario", foreign_keys=[id_medico])
    paciente = relationship("Paciente", foreign_keys=[id_paciente])
    prescripcion = relationship("Prescripcion", foreign_keys=[id_prescripcion])


class Reserva(Base):
    __tablename__ = "reserva"

    id_reserva = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    id_paciente = Column(UUID(as_uuid=True), ForeignKey("paciente.id_paciente"))
    fecha = Column(TIMESTAMP)
    estado = Column(String(50))


class ReservaMedicamento(Base):
    __tablename__ = "reserva_medicamento"

    id_reserva = Column(UUID(as_uuid=True), ForeignKey("reserva.id_reserva"), primary_key=True)
    id_medicamento = Column(UUID(as_uuid=True), ForeignKey("medicamento.id_medicamento"), primary_key=True)
    cantidad = Column(Integer)


class Entrega(Base):
    __tablename__ = "entrega"

    id_receta = Column(UUID(as_uuid=True), ForeignKey("receta.id_receta"), primary_key=True)
    id_funcionario = Column(UUID(as_uuid=True), ForeignKey("usuario.id"))
    fecha = Column(TIMESTAMP)
    estado = Column(String(50))
    rut_retiro = Column(String(20))
    nombre_retiro = Column(String(100))
