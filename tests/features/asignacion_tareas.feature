# Created by ximen at 10/1/2026
# language: es

@tareas @asignacion
Característica: Asignación de tareas a asesores
  Como supervisor
  Quiero asignar y gestionar tareas
  Para asegurar el seguimiento del trabajo de los asesores

  Antecedentes:
    Dado que existe un supervisor autenticado con correo "supervisor@sistema.com"
    Y existe un asesor con identificador "ASE-001" y correo "asesor@sistema.com"

  Escenario: Asignar una tarea a un asesor
    Dado que existe una tarea con código "TAR-001" y prioridad "Media"
    Cuando el supervisor asigna la tarea "TAR-001" al asesor "ASE-001"
    Entonces la tarea "TAR-001" queda asignada al asesor "ASE-001"
    Y la tarea tiene estado "Asignada"

  Escenario: Asignar múltiples tareas a un asesor
    Dado que el asesor "ASE-001" tiene tareas previamente asignadas
      | codigo   |
      | TAR-002  |
      | TAR-003  |
    Y existe una tarea con código "TAR-004" y prioridad "Alta"
    Cuando el supervisor asigna la tarea "TAR-004" al asesor "ASE-001"
    Entonces el asesor "ASE-001" mantiene sus tareas anteriores
    Y el asesor "ASE-001" tiene asignada la tarea "TAR-004"

  Escenario: Asignar una tarea con fecha de vencimiento
    Dado que existe una tarea con código "TAR-005" y prioridad "Alta"
    Cuando el supervisor asigna la tarea "TAR-005" al asesor "ASE-001" con fecha de vencimiento "2026-01-20"
    Entonces la tarea "TAR-005" registra la fecha de vencimiento "2026-01-20"

  Escenario: Enviar notificación al asesor
    Dado que la tarea "TAR-006" está asignada al asesor "ASE-001"
    Cuando el proceso de asignación finaliza
    Entonces el asesor "ASE-001" recibe una notificación de nueva tarea

  Escenario: Enviar recordatorio antes del vencimiento
    Dado que la tarea "TAR-007" está asignada al asesor "ASE-001" con fecha de vencimiento "2026-01-20"
    Cuando se alcanza 24 horas antes de la fecha de vencimiento
    Entonces el sistema envía un recordatorio al asesor "ASE-001"

  Escenario: Cambiar estado de una tarea
    Dado que la tarea "TAR-008" está asignada al asesor "ASE-001"
    Cuando el asesor cambia el estado de la tarea a "Completada"
    Entonces la tarea "TAR-008" queda en estado "Completada"

  Escenario: Editar una tarea asignada
    Dado que la tarea "TAR-009" está asignada al asesor "ASE-001"
    Cuando el supervisor actualiza la prioridad de la tarea a "Alta"
    Entonces la tarea "TAR-009" refleja la prioridad "Alta"
