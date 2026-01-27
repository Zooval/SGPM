# Created by Henry at 9/1/2026
# language: es

@citas
Característica: Reservación de citas con solicitantes
  Como asesor
  Quiero gestionar citas con los solicitantes
  Para atender eficientemente sus procesos migratorios

  Antecedentes:
    Dado que el asesor "Juan Pérez" está autenticado
    Y existe un solicitante "María López" con cédula "ABC123"
    Y existe una solicitud migratoria con código "SOL-001" del solicitante "ABC123" gestionada por el asesor "Juan Pérez"

  @crear_cita
  Escenario: Creación de una cita válida
    Cuando el asesor agenda una cita de tipo "ASESORIA" para la solicitud "SOL-001" desde "2026-04-19 10:00" hasta "2026-04-19 10:30" con observación "Primera revisión"
    Entonces la cita queda en estado "PROGRAMADA"
    Y la cita queda asociada a la solicitud "SOL-001"

  @conflicto_horario
  Escenario: Prevención de conflictos de horario
    Dado que el asesor tiene una cita "PROGRAMADA" desde "2026-04-19 10:00" hasta "2026-04-19 10:30"
    Cuando el asesor intenta agendar otra cita para "2026-04-19 10:00" hasta "2026-04-19 10:30"
    Entonces se informa que el horario no está disponible
    Y no se agenda la cita

  @ver_agenda
  Escenario: Visualización de la cita en la agenda
    Dado que existe una cita "PROGRAMADA" para la solicitud "SOL-001" desde "2026-04-19 10:00" hasta "2026-04-19 10:30"
    Cuando el asesor consulta su agenda del día "2026-04-19"
    Entonces visualiza la cita a las "10:00" asociada al solicitante "María López"

  @reprogramar_cita
  Escenario: Modificación de una cita existente
    Dado que existe una cita "PROGRAMADA" desde "2026-04-19 10:00" hasta "2026-04-19 10:30"
    Cuando el asesor reprograma la cita a "2026-04-20 11:30" hasta "2026-04-20 12:00" con observación "Cambio por disponibilidad"
    Entonces la cita queda en estado "REPROGRAMADA"
    Y la cita refleja el nuevo rango de fecha y hora

  @cancelar_cita
  Escenario: Cancelación de una cita
    Dado que existe una cita "REPROGRAMADA" desde "2026-04-20 11:30" hasta "2026-04-20 12:00"
    Cuando el asesor cancela la cita con observación "Solicitante no podrá asistir"
    Entonces la cita queda en estado "CANCELADA"

  @notificacion_solicitante
  Escenario: Notificación al solicitante por cita creada o modificada
    Dado que existe una cita para la solicitud "SOL-001"
    Cuando la cita es creada o reprogramada
    Entonces el solicitante recibe una notificación de tipo "CITA_PROXIMA"
    Y la notificación incluye la fecha y hora de la cita

  @recordatorio_asesor
  Escenario: Recordatorio al asesor 24 horas antes de la cita
    Dado que existe una cita "PROGRAMADA" para "2026-04-19 10:00"
    Y faltan 24 horas para la cita
    Entonces el asesor responsable recibe una notificación de tipo "RECORDATORIO"
    Y la notificación incluye la fecha y hora de la cita
