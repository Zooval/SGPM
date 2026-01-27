# Created by Fernando at 10/1/2026
# language: es

@reportes @estadisticas
Característica: Generación de reportes de estadísticas de tareas
  Como supervisor
  Quiero generar reportes estadísticos de las tareas
  Para analizar el desempeño y la carga de trabajo de los asesores

  Antecedentes:
    Dado que el supervisor con correo "supervisor@sistema.com" está autenticado
    Y existe el asesor con correo "asesor@sistema.com"
    Y existen tareas asignadas al asesor con correo "asesor@sistema.com" con distintos estados, prioridades y vencimientos

  Escenario: Generar reporte por asesor en un periodo
    Cuando el supervisor genera un reporte de tareas para el asesor con correo "asesor@sistema.com" desde "2026-01-01 00:00" hasta "2026-01-31 23:59"
    Entonces el reporte muestra el total de tareas del asesor con correo "asesor@sistema.com" dentro del periodo
    Y el reporte desglosa las tareas por estado "PENDIENTE", "EN_PROGRESO", "COMPLETADA" y "CANCELADA"
    Y el reporte desglosa las tareas por prioridad "BAJA", "MEDIA", "ALTA" y "CRITICA"

  Escenario: Generar reporte global en un periodo
    Cuando el supervisor genera un reporte global de tareas desde "2026-01-01 00:00" hasta "2026-01-31 23:59"
    Entonces el reporte muestra el total de tareas del periodo
    Y el reporte desglosa las tareas por estado "PENDIENTE", "EN_PROGRESO", "COMPLETADA" y "CANCELADA"
    Y el reporte desglosa las tareas por prioridad "BAJA", "MEDIA", "ALTA" y "CRITICA"

  Escenario: Identificar tareas vencidas al momento del reporte
    Dado que existe una tarea "PENDIENTE" asignada al asesor con correo "asesor@sistema.com" con vencimiento "2026-01-20 17:00"
    Cuando el supervisor genera un reporte de tareas vencidas al momento "2026-01-21 10:00"
    Entonces el reporte incluye la tarea como "VENCIDA"
    Y el reporte muestra la cantidad total de tareas vencidas por asesor

  Escenario: Comparar desempeño por tareas completadas
    Dado que existen tareas en estado "COMPLETADA" registradas para distintos asesores en el periodo desde "2026-01-01 00:00" hasta "2026-01-31 23:59"
    Cuando el supervisor genera un reporte de desempeño por tareas completadas desde "2026-01-01 00:00" hasta "2026-01-31 23:59"
    Entonces el reporte muestra el total de tareas "COMPLETADA" por asesor
    Y el reporte presenta a los asesores ordenados de mayor a menor según tareas "COMPLETADA"

  Escenario: Exportar un reporte generado
    Dado que el supervisor tiene un reporte generado para el periodo desde "2026-01-01 00:00" hasta "2026-01-31 23:59"
    Cuando el supervisor solicita exportar el reporte en formato "PDF"
    Entonces se obtiene el reporte exportado en formato "PDF"
    Y el reporte exportado conserva los totales y desgloses del reporte generado
