# Created by ximen at 9/1/2026
# language: es

Característica: Gestión de citas migratorias
  Como empleado migratorio
  Quiero crear, visualizar, modificar y cancelar citas
  Para organizar eficientemente la atención a los migrantes

Antecedentes:
  Dado que el empleado Juan Pérez se encuentra autenticado en el sistema
  Y existe un migrante registrado con nombre "María López" y documento "ABC123"
  Y el sistema de gestión de citas se encuentra disponible

Escenario: Creación de una cita válida
  Cuando el empleado reserva una cita para el migrante "María López"
  Y ingresa la fecha "19-04-2025" y la hora "10:00"
  Entonces la cita queda registrada asociada al migrante
  Y la cita tiene como responsable al empleado "Juan Pérez"

Escenario: Prevención de conflictos de horario
  Dado que el empleado tiene una cita registrada el día "19-04-2025" a las "10:00"
  Cuando intenta reservar otra cita para el mismo día "19-04-2025" a las "10:00"
  Entonces el sistema impide la reserva
  Y solicita seleccionar un horario diferente

Escenario: Visualización de la cita en la agenda
  Dado que existe una cita registrada para el migrante "María López"
  Cuando el empleado consulta la agenda del día "19-04-2025"
  Entonces la cita se muestra a las "10:00" asociada al migrante "María López"

Escenario: Modificación de una cita existente
  Dado que existe una cita registrada el día "19-04-2025" a las "10:00"
  Cuando el empleado modifica la cita a la fecha "20-04-2025" y hora "11:30"
  Entonces la cita se actualiza correctamente
  Y el cambio queda registrado en el historial de la cita

Escenario: Cancelación de una cita
  Dado que existe una cita registrada para el día "20-04-2025" a las "11:30"
  Cuando el empleado cancela la cita
  Entonces la cita deja de estar activa
  Y la cancelación queda registrada en el sistema

