-- Insertar Usuarios
INSERT INTO Usuario (RUT, nombre, contrasena, rol) VALUES
('11111111-1', 'Dr. Juan Pérez', 'medico123', 'medico'),
('22222222-2', 'Dra. Ana Gómez', 'medico123', 'medico'),
('33333333-3', 'Laura Campos', 'func123', 'funcionario'),
('44444444-4', 'Carlos Díaz', 'func123', 'funcionario');

-- Insertar Pacientes
INSERT INTO Paciente (RUT, nombre, numero, correo) VALUES
('55555555-5', 'Mateo Silva', 987654321, 'mateo@gmail.com'),
('66666666-6', 'Sofía Herrera', 123456789, 'sofia@gmail.com');

-- Insertar Turnos
INSERT INTO Turno (nombre, fecha_inicio, fecha_fin) VALUES
('Turno Mañana', '2025-05-20 08:00:00', '2025-05-20 14:00:00'),
('Turno Tarde', '2025-05-20 14:00:00', '2025-05-20 20:00:00');

-- Insertar Boxes
INSERT INTO Box (nombre, piso) VALUES
('Box 101', 1),
('Box 102', 1);

-- Asignar médicos a turnos y boxes (Asistencia)
INSERT INTO Asistencia (ID_medico, ID_turno, ID_box)
SELECT u.ID, t.ID_turno, b.ID_box
FROM Usuario u, Turno t, Box b
WHERE u.nombre = 'Dr. Juan Pérez' AND t.nombre = 'Turno Mañana' AND b.nombre = 'Box 101';

-- Insertar Principios Activos
INSERT INTO Principio_activo (nombre, categoria) VALUES
('Paracetamol', 'Analgésico'),
('Amoxicilina', 'Antibiótico');

-- Insertar Medicamentos con su código de barras, dosis y vía de administración
INSERT INTO Medicamento (nombre, codigo_barras, dosis_concentracion, via_administracion) VALUES
('Dolocam', gen_random_uuid(), '500mg', 'Oral'),
('Amoxil', gen_random_uuid(), '250mg', 'Oral');

-- Relación Medicamento - Principio activo
INSERT INTO Medicamento_principio (ID_medicamento, ID_principio)
SELECT m.ID_medicamento, p.ID_principio
FROM Medicamento m, Principio_activo p
WHERE (m.nombre = 'Dolocam' AND p.nombre = 'Paracetamol')
   OR (m.nombre = 'Amoxil' AND p.nombre = 'Amoxicilina');

-- Insertar lote para el medicamento Dolocam
INSERT INTO Medicamento_lote (
    ID_medicamento, lote, fecha_vencimiento, cantidad, cantidad_reservada,
    cantidad_defectuosa, cantidad_en_idea, cantidad_en_estado, cantidad_envase_roto
)
SELECT m.ID_medicamento, 'LOTE-001', '2026-01-01', 100, 5,
       2, 0, 0, 1
FROM Medicamento m
WHERE m.nombre = 'Dolocam';

-- Insertar Prescripción
INSERT INTO Prescripcion (ID_medico, ID_paciente)
SELECT u.ID, p.ID_paciente
FROM Usuario u, Paciente p
WHERE u.nombre = 'Dr. Juan Pérez' AND p.nombre = 'Mateo Silva';

-- Añadir principios activos a la prescripción
INSERT INTO Prescripcion_principio (ID_prescripcion, ID_principio, duracion, frecuencia)
SELECT pr.ID_prescripcion, pa.ID_principio, '5 días', 'cada 8 horas'
FROM Prescripcion pr, Principio_activo pa
WHERE pa.nombre = 'Paracetamol'
LIMIT 1;

-- Crear Receta
INSERT INTO Receta (ID_prescripcion, ID_paciente, ID_medico, fecha_emision, estado)
SELECT pr.ID_prescripcion, pa.ID_paciente, pr.ID_medico, '2025-05-20 09:00:00', 'emitida'
FROM Prescripcion pr
JOIN Paciente pa ON pa.nombre = 'Mateo Silva'
LIMIT 1;

-- Crear Reserva
INSERT INTO Reserva (ID_paciente, fecha, estado)
SELECT p.ID_paciente, '2025-05-21 10:00:00', 'pendiente'
FROM Paciente p
WHERE p.nombre = 'Mateo Silva';

-- Asociar medicamentos a reserva
INSERT INTO Reserva_medicamento (ID_reserva, ID_medicamento, cantidad)
SELECT r.ID_reserva, m.ID_medicamento, 2
FROM Reserva r, Medicamento m
WHERE r.ID_paciente = (SELECT ID_paciente FROM Paciente WHERE nombre = 'Mateo Silva')
  AND m.nombre = 'Dolocam'
LIMIT 1;

-- Entregar la receta
INSERT INTO Entrega (ID_receta, ID_funcionario, fecha, estado, RUT_retiro, nombre_retiro)
SELECT re.ID_receta, u.ID, '2025-05-20 11:00:00', 'entregado', '12345678-9', 'Juan Retiro'
FROM Receta re, Usuario u
WHERE u.nombre = 'Laura Campos' AND re.ID_paciente = (SELECT ID_paciente FROM Paciente WHERE nombre = 'Mateo Silva')
LIMIT 1;
