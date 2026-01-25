# Created by ximen at 10/1/2026
# language: es

Característica: Asignación de tareas
  Como supervisor del sistema
  Quiero asignar y gestionar tareas
  Para controlar el trabajo de los asesores

  Escenario: Asignar una tarea a un asesor
    Dado que un supervisor ha iniciado sesión
    Y existe un asesor registrado
    Cuando el supervisor asigna una tarea al asesor
    Entonces la tarea queda registrada en el sistema
    Y la tarea tiene estado "PENDIENTE"

  Escenario: Asignar múltiples tareas a un asesor
    Dado que un supervisor ha iniciado sesión
    Y un asesor tiene tareas previamente asignadas
    Cuando el supervisor asigna una nueva tarea al asesor
    Entonces el sistema registra la nueva tarea
    Y las tareas anteriores del asesor se mantienen

  Escenario: Asignar una tarea con fecha de vencimiento
    Dado que un supervisor está asignando una tarea
    Cuando el supervisor ingresa una fecha de vencimiento
    Y guarda la tarea
    Entonces la tarea se guarda con una fecha de vencimiento a 24 horas

  Escenario: Enviar notificación al asesor
    Dado que una tarea ha sido asignada a un asesor
    Cuando la asignación se completa
    Entonces el asesor recibe una notificación de la nueva tarea

  Escenario: Enviar recordatorio al asesor
    Dado que un asesor tiene una tarea asignada
    Y la tarea tiene una fecha de vencimiento definida
    Cuando faltan 24 horas para el vencimiento
    Entonces el sistema envía un recordatorio al asesor

  Escenario: Cambiar estado de una tarea
    Dado que un asesor tiene una tarea asignada
    Cuando el asesor cambia el estado de la tarea
    Entonces el sistema guarda el nuevo estado de la tarea

  Escenario: Editar una tarea asignada
    Dado que existe una tarea asignada a un asesor
    Cuando el supervisor edita la información de la tarea
    Entonces el sistema guarda los cambios realizados
