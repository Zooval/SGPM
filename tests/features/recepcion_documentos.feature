# language: es

Característica: Reprogramación de citas migratorias

  HU 6 – Reprogramación de citas desde calendario centralizado
  Como asesor migratorio,
  quiero reprogramar citas desde un calendario centralizado,
  para mantener una agenda actualizada y notificar oportunamente al migrante.

  Esquema del escenario: Reprogramación exitosa de cita de visa
    Dado que existe una cita de visa con ID "<id_cita>" agendada para "<fecha_actual>"
    Y que la fecha "<nueva_fecha>" se encuentra disponible en el calendario
    Cuando el asesor reprograma la cita "<id_cita>" para la "<nueva_fecha>"
    Entonces el sistema debe registrar la nueva fecha "<nueva_fecha>" en la base de datos
    Y se debe disparar un evento de notificación para el usuario e inmigrante
    Y la cita debe conservar su categoría de trámite "<tipo_tramite>"

    Ejemplos:
      | id_cita | fecha_actual     | nueva_fecha      | tipo_tramite |
      | V-101   | 2023-11-01 09:00 | 2023-11-01 15:00 | Visa_Turismo |
      | V-102   | 2023-11-02 10:30 | 2023-11-03 08:00 | Visa_Trabajo |

  Esquema del escenario: Fallo al reprogramar una cita por conflicto de horarios
    Dado que existe una cita "Cita_A" programada para las "<hora_original>"
    Y que existe otro evento "Evento_B" ya confirmado a las "<hora_destino>"
    Cuando el asesor intenta reprogramar la "Cita_A" para las "<hora_destino>"
    Entonces el sistema debe lanzar un error de tipo "<tipo_error>"
    Y la "Cita_A" debe permanecer agendada a las "<hora_original>"

    Ejemplos:
      | hora_original    | hora_destino     | tipo_error         |
      | 2023-10-27 09:00 | 2023-10-27 10:00 | SlotNotAvailable   |
      | 2023-10-28 14:00 | 2023-10-28 15:30 | OverlapConflict    |

  Esquema del escenario: Rechazo de modificación por privilegios insuficientes
    Dado que el usuario activo tiene el rol de "<rol_asignado>"
    Y existe una cita activa con ID "<id_cita>"
    Cuando el usuario intenta ejecutar la acción de "Reprogramar" sobre la cita "<id_cita>"
    Entonces el sistema debe rechazar la solicitud
    Y se debe mostrar el mensaje de error: "<mensaje_esperado>"
    Y el sistema debe escribir una entrada en el Log de Auditoría con el código "<codigo_evento>"

    Ejemplos:
      | rol_asignado | id_cita | mensaje_esperado                                         | codigo_evento     |
      | Solo_Lectura | C-500   | Usted no tiene permisos para modificar citas migratorias | AUTH_UNAUTHORIZED |
      | Auditor      | C-501   | Acción denegada: Su perfil es de consulta únicamente     | AUTH_FORBIDDEN    |

#  Esquema del escenario: Recálculo de recordatorios tras reprogramación
#    Dado que existe una cita originalmente agendada para el "<fecha_vieja>"
#    Y existe un recordatorio pendiente programado para el "<recordatorio_viejo>"
#    Y la documentación del migrante tiene fecha de vencimiento el "<vencimiento_doc>"
#    Cuando la cita es reprogramada exitosamente para el "<fecha_nueva>"
#    Entonces el recordatorio de la fecha "<recordatorio_viejo>" debe pasar a estado "CANCELADO"
#    Y se debe programar un nuevo recordatorio para el "<nuevo_recordatorio>"
#
#    Ejemplos:
#      | fecha_vieja      | recordatorio_viejo | fecha_nueva      | vencimiento_doc  | nuevo_recordatorio |
#      | 2023-12-10 10:00 | 2023-12-09 10:00   | 2023-12-20 10:00 | 2024-01-01 00:00 | 2023-12-19 10:00   |
#      | 2023-12-15 14:00 | 2023-12-13 14:00   | 2024-02-01 09:00 | 2024-03-01 00:00 | 2024-01-30 09:00   |

