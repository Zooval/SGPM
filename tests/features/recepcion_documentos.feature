# language: es

Característica: Reprogramación de citas migratorias

  HU 6 – Reprogramación de citas desde calendario centralizado
  Como asesor migratorio,
  quiero reprogramar citas desde un calendario centralizado,
  para mantener una agenda actualizada y notificar oportunamente al migrante.

  Esquema del escenario: Cambio exitoso de horario para una cita de visa.
    Dado que el asesor ha iniciado sesión en el CRM y accede al calendario centralizado (Scheduler).
    Y existe una cita de visa programada para un inmigrante en una fecha específica.
    Cuando el asesor arrastra la cita a un nuevo bloque de tiempo disponible en el calendario.
    Entonces el sistema debe actualizar la fecha y hora de la cita en la base de datos de forma sincronizada.
    Y el sistema debe enviar automáticamente una notificación de reprogramación al inmigrante y al asesor asignado.
    Y el evento debe mantener su código de color para diferenciar el tipo de trámite.

  Esquema del escenario: Intento de reprogramación en un horario ocupado.
    Dado que el asesor intenta mover una cita a un horario que ya contiene otro evento programado.
    Cuando el asesor confirma el cambio de horario.
    Entonces el sistema debe mostrar un mensaje de error indicando que el horario no está disponible.
    Y el sistema debe revertir la cita a su posición original en el calendario, impidiendo el conflicto de horarios.

  Esquema del escenario: Usuario sin permisos intenta reprogramar una cita.
    Dado que un usuario con rol de "Solo Lectura" ha iniciado sesión en el sistema.
    Cuando el usuario intenta editar o mover una cita en el calendario centralizado.
    Entonces el sistema debe bloquear la acción de edición.
    Y debe mostrar un mensaje de aviso: "Usted no tiene permisos para modificar citas migratorias".
    Y el sistema debe generar un registro en el log de auditoría detallando el intento de modificación.

  Esquema del escenario: Sincronización de alertas automáticas tras el cambio de fecha.
    Dado que una cita ha sido reprogramada exitosamente para una nueva fecha futura.
    Cuando el sistema procesa las tareas de fondo para notificaciones.
    Entonces el sistema debe cancelar los recordatorios previos asociados a la fecha antigua.
    Y debe programar nuevos recordatorios automáticos basados en la nueva fecha de la cita y la fecha de expiración de la documentación del migrante



