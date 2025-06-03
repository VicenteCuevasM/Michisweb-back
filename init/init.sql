-- Habilitar extensión para generar UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tabla Usuario con campo 'rol'
CREATE TABLE Usuario (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    RUT VARCHAR(20) NOT NULL,
    nombre VARCHAR(100),
    contrasena VARCHAR(100),
    rol VARCHAR(50) NOT NULL  -- Ej: 'medico', 'funcionario'
);

-- Tabla Turno
CREATE TABLE Turno (
    ID_turno UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100),
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP
);

-- Tabla Box
CREATE TABLE Box (
    ID_box UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100),
    piso INT
);

-- Tabla Asistencia
CREATE TABLE Asistencia (
    ID_asistencia UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ID_medico UUID REFERENCES Usuario(ID),
    ID_turno UUID REFERENCES Turno(ID_turno),
    ID_box UUID REFERENCES Box(ID_box)
);

-- Tabla Paciente
CREATE TABLE Paciente (
    ID_paciente UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    RUT VARCHAR(20) NOT NULL,
    nombre VARCHAR(100),
    numero INT,
    correo VARCHAR(100)
);

-- Tabla Principio_activo
CREATE TABLE Principio_activo (
    ID_principio UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100),
    categoria VARCHAR(100)
);

-- Tabla Medicamento
CREATE TABLE Medicamento (
    ID_medicamento UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(255),
    codigo_barras UUID UNIQUE,
    dosis_concentracion VARCHAR(100),
    via_administracion VARCHAR(100)
);

-- Tabla Medicamento_principio
CREATE TABLE Medicamento_principio (
    ID_medicamento UUID REFERENCES Medicamento(ID_medicamento),
    ID_principio UUID REFERENCES Principio_activo(ID_principio),
    PRIMARY KEY (ID_medicamento, ID_principio)
);

-- Tabla Medicamento_lote
CREATE TABLE Medicamento_lote (
    id_lote UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ID_medicamento UUID REFERENCES Medicamento(ID_medicamento),
    lote VARCHAR(50),
    fecha_vencimiento TIMESTAMP,
    cantidad INT,
    cantidad_defectuosa INT,
    cantidad_en_idea INT,
    cantidad_en_estado INT,
    cantidad_envase_roto INT
);

-- Tabla Prescripcion
CREATE TABLE Prescripcion (
    ID_prescripcion UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ID_medico UUID REFERENCES Usuario(ID),
    ID_paciente UUID REFERENCES Paciente(ID_paciente)
);

-- Tabla Prescripcion_principio
CREATE TABLE Prescripcion_principio (
    ID_prescripcion UUID REFERENCES Prescripcion(ID_prescripcion),
    ID_principio UUID REFERENCES Principio_activo(ID_principio),
    duracion VARCHAR(100),
    frecuencia VARCHAR(100),
    PRIMARY KEY (ID_prescripcion, ID_principio)
);

-- Tabla Receta
CREATE TABLE Receta (
    ID_receta UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ID_prescripcion UUID REFERENCES Prescripcion(ID_prescripcion),
    ID_paciente UUID REFERENCES Paciente(ID_paciente),
    ID_medico UUID REFERENCES Usuario(ID),
    fecha_emision TIMESTAMP,
    estado VARCHAR(50)
);

-- Tabla Reserva
CREATE TABLE Reserva (
    ID_reserva UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ID_paciente UUID REFERENCES Paciente(ID_paciente),
    fecha TIMESTAMP,
    estado VARCHAR(50)
);

-- Tabla Reserva_medicamento
CREATE TABLE Reserva_medicamento (
    ID_reserva UUID REFERENCES Reserva(ID_reserva),
    ID_medicamento UUID REFERENCES Medicamento(ID_medicamento),
    cantidad INT,
    PRIMARY KEY (ID_reserva, ID_medicamento)
);

-- Tabla Entrega
CREATE TABLE Entrega (
    ID_receta UUID PRIMARY KEY REFERENCES Receta(ID_receta),
    ID_funcionario UUID REFERENCES Usuario(ID),
    fecha TIMESTAMP,
    estado VARCHAR(50),
    RUT_retiro VARCHAR(20),
    nombre_retiro VARCHAR(100)
);
