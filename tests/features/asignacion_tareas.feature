# Created by Emilia at 10/1/2026
# language: es

@tareas @asignacion
Característica: Asignación de tareas a asesores
  Como supervisor
  Quiero asignar y gestionar tareas
  Para asegurar el seguimiento del trabajo de los asesores

  Antecedentes:
    Dado que existe un supervisor autenticado con correo "supervisor@sistema.com"
    Y existe un asesor con correo "asesor@sistema.com"

  Escenario: Asignar una tarea a un asesor
    Dado que existe una tarea con código "TAR-001" y prioridad "MEDIA"
    Cuando el supervisor asigna la tarea "TAR-001" al asesor con correo "asesor@sistema.com"
    Entonces la tarea "TAR-001" queda asignada al asesor con correo "asesor@sistema.com"
    Y la tarea "TAR-001" tiene estado "PENDIENTE"

  Escenario: Asignar múltiples tareas a un asesor
    Dado que el asesor con correo "asesor@sistema.com" tiene tareas previamente asignadas
      | codigo   |
      | TAR-002  |
      | TAR-003  |
    Y existe una tarea con código "TAR-004" y prioridad "ALTA"
    Cuando el supervisor asigna la tarea "TAR-004" al asesor con correo "asesor@sistema.com"
    Entonces el asesor con correo "asesor@sistema.com" mantiene sus tareas anteriores
    Y la tarea "TAR-004" queda asignada al asesor con correo "asesor@sistema.com"

  Escenario: Asignar una tarea con fecha de vencimiento
    Dado que existe una tarea con código "TAR-005" y prioridad "ALTA"
    Cuando el supervisor asigna la tarea "TAR-005" al asesor con correo "asesor@sistema.com" con fecha de vencimiento "2026-01-20 17:00"
    Entonces la tarea "TAR-005" registra la fecha de vencimiento "2026-01-20 17:00"
    Y la tarea "TAR-005" queda asignada al asesor con correo "asesor@sistema.com"

  Escenario: Enviar notificación al asesor por tarea asignada
    Dado que la tarea "TAR-006" está asignada al asesor con correo "asesor@sistema.com"
    Cuando el proceso de asignación finaliza
    Entonces el asesor con correo "asesor@sistema.com" recibe una notificación de tipo "ASIGNACION_TAREA"

  Escenario: Enviar recordatorio antes del vencimiento
    Dado que la tarea "TAR-007" está asignada al asesor con correo "asesor@sistema.com" con fecha de vencimiento "2026-01-20 17:00"
    Cuando se alcanza 24 horas antes de la fecha de vencimiento
    Entonces el asesor con correo "asesor@sistema.com" recibe una notificación de tipo "RECORDATORIO"

  Escenario: Cambiar estado de una tarea
    Dado que la tarea "TAR-008" está asignada al asesor con correo "asesor@sistema.com"
    Cuando el asesor cambia el estado de la tarea "TAR-008" a "COMPLETADA"
    Entonces la tarea "TAR-008" queda en estado "COMPLETADA"

  Escenario: Editar una tarea asignada
    Dado que la tarea "TAR-009" está asignada al asesor con correo "asesor@sistema.com"
    Cuando el supervisor actualiza la prioridad de la tarea "TAR-009" a "ALTA"
    Entonces la tarea "TAR-009" refleja la prioridad "ALTA"
