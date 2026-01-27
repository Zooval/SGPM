# Created by Joel at 10/01/2026
# language: es

@solicitudes @estado_fechas
Característica: Control de estado y fechas clave de una solicitud
  Como asesor
  Quiero actualizar el estado y registrar fechas clave de una solicitud
  Para dar seguimiento, evitar inconsistencias y mantener trazabilidad

  Antecedentes:
    Dado que existe un solicitante con los siguientes datos:
      | cedula     | nombres     | apellidos      | correo           | telefono   | direccion        | fecha_nacimiento | habilitado |
      | 0912345678 | Juan Carlos | Mendoza Ruiz   | cliente@mail.com | 099999999 | Av. Siempre Viva | 1995-06-15       | true       |

    Y que existe un asesor con los siguientes datos:
      | nombres      | apellidos     | email_asesor         | rol    |
      | Andrea Sofía | López Torres  | asesor@agencia.com   | ASESOR |

    Y que existe una solicitud migratoria con los siguientes datos:
      | codigo        | tipo_servicio | estado_actual | fecha_creacion | fecha_expiracion |
      | SOL-2026-0001 | VISA_TRABAJO  | CREADA        | 2026-01-10     | 2026-12-31       |

    Y la solicitud "SOL-2026-0001" pertenece al solicitante con cédula "0912345678"
    Y la solicitud "SOL-2026-0001" es gestionada por el asesor "asesor@agencia.com"
    Y el asesor se encuentra autenticado en el sistema

  @estado @avance_valido
  Esquema del escenario: Cambiar a un estado permitido registra el cambio y actualiza la fecha
    Dado que la solicitud "SOL-2026-0001" se encuentra en estado "<estado_inicial>"
    Y la transición de "<estado_inicial>" a "<estado_nuevo>" está permitida
    Cuando el asesor cambia el estado de la solicitud con los siguientes datos:
      | nuevo_estado | motivo  |
      | <estado_nuevo> | <motivo> |
    Entonces la solicitud visualiza el estado_actual como "<estado_nuevo>"
    Y la solicitud visualiza la fecha de última actualización como "<fecha_evento>"
    Y el historial de estados registra:
      | usuario            | estado_anterior | estado_nuevo | fecha          | motivo  |
      | asesor@agencia.com | <estado_inicial> | <estado_nuevo> | <fecha_evento> | <motivo> |

    Ejemplos:
      | estado_inicial | estado_nuevo | motivo                 | fecha_evento |
      | CREADA         | EN_REVISION  | Verificación inicial   | 2026-01-10   |
      | EN_REVISION    | ENVIADA      | Documentos completos   | 2026-01-10   |
      | ENVIADA        | APROBADA     | Respuesta favorable    | 2026-01-10   |

  @estado @avance_invalido
  Esquema del escenario: Evitar una transición no permitida mantiene el estado
    Dado que la solicitud "SOL-2026-0001" se encuentra en estado "<estado_inicial>"
    Y la transición de "<estado_inicial>" a "<estado_nuevo>" no está permitida
    Cuando el asesor intenta cambiar el estado con los siguientes datos:
      | nuevo_estado | motivo |
      | <estado_nuevo> | <motivo> |
    Entonces la solicitud mantiene el estado_actual como "<estado_inicial>"
    Y el sistema muestra el mensaje "<mensaje_error>"
    Y el historial de estados no registra ningún cambio

    Ejemplos:
      | estado_inicial | estado_nuevo | motivo              | mensaje_error                          |
      | CREADA         | APROBADA     | Saltar revisión     | No se permite la transición solicitada |
      | APROBADA       | EN_REVISION  | Reabrir análisis    | No se permite la transición solicitada |

  @estado @rechazo_requiere_motivo
  Esquema del escenario: Rechazar una solicitud exige motivo obligatorio
    Dado que la solicitud "SOL-2026-0001" se encuentra en estado "<estado_inicial>"
    Y la transición a estado "RECHAZADA" está permitida
    Cuando el asesor intenta cambiar el estado con los siguientes datos:
      | nuevo_estado | motivo |
      | RECHAZADA    | <motivo> |
    Entonces el resultado del cambio es "<resultado>"
    Y si el resultado es "rechazado", el sistema muestra el mensaje "<mensaje_error>"

    Ejemplos:
      | estado_inicial | motivo                   | resultado | mensaje_error                        |
      | EN_REVISION    | Documentación incompleta | aceptado  |                                      |
      | EN_REVISION    |                          | rechazado | El motivo es obligatorio al rechazar |

  @estado @archivada_bloquea
  Esquema del escenario: Una solicitud archivada no permite modificaciones
    Dado que la solicitud "SOL-2026-0001" se encuentra en estado "CERRADA"
    Cuando el asesor intenta cambiar el estado con los siguientes datos:
      | nuevo_estado | motivo |
      | <estado_nuevo> | <motivo> |
    Entonces la solicitud mantiene el estado_actual como "CERRADA"
    Y el sistema muestra el mensaje "<mensaje_error>"
    Y el historial de estados no registra cambios

    Ejemplos:
      | estado_nuevo | motivo          | mensaje_error                       |
      | EN_REVISION  | Retomar trámite | No se permiten cambios en CERRADA   |
      | RECHAZADA    | Cerrar trámite  | No se permiten cambios en CERRADA   |

  @fechas @registrar_fecha
  Esquema del escenario: Registrar una fecha clave válida actualiza la solicitud
    Dado que "<tipo_fecha>" es un campo de fecha permitido del proceso
    Y la fecha "<fecha_valor>" es igual o posterior a la fecha de creación "2026-01-10"
    Cuando el asesor asigna la fecha con los siguientes datos:
      | campo        | valor        |
      | <tipo_fecha> | <fecha_valor> |
    Entonces la solicitud visualiza "<tipo_fecha>" como "<fecha_valor>"
    Y la solicitud visualiza la fecha de última actualización como "<fecha_evento>"
    Y el historial de fechas registra:
      | usuario            | campo        | valor_anterior | valor_nuevo  | fecha_evento |
      | asesor@agencia.com | <tipo_fecha> | <valor_anterior> | <fecha_valor> | <fecha_evento> |

    Ejemplos:
      | tipo_fecha          | valor_anterior | fecha_valor  | fecha_evento |
      | fechaRecepcionDocs  | (vacío)        | 2026-01-11   | 2026-01-10   |
      | fechaEnvioSolicitud | (vacío)        | 2026-01-15   | 2026-01-10   |
      | fechaCita           | (vacío)        | 2026-01-18   | 2026-01-10   |

  @fechas @fecha_invalida
  Esquema del escenario: Bloquear una fecha anterior a la creación
    Dado que "<tipo_fecha>" es un campo de fecha permitido del proceso
    Y la fecha "<fecha_valor>" es anterior a la fecha de creación "2026-01-10"
    Cuando el asesor asigna la fecha con los siguientes datos:
      | campo        | valor        |
      | <tipo_fecha> | <fecha_valor> |
    Entonces el sistema muestra el mensaje "<mensaje_error>"
    Y la solicitud mantiene el valor anterior de "<tipo_fecha>"

    Ejemplos:
      | tipo_fecha         | fecha_valor  | mensaje_error                                         |
      | fechaRecepcionDocs | 2026-01-05   | La fecha no puede ser anterior a la fecha de creación |
      | fechaCita          | 2026-01-01   | La fecha no puede ser anterior a la fecha de creación |

  @fechas @coherencia_fechas
  Esquema del escenario: Validar coherencia entre fechas
    Dado que la solicitud visualiza "fechaRecepcionDocs" como "<fecha_recepcion>"
    Cuando el asesor asigna "fechaEnvioSolicitud" con valor "<fecha_envio>"
    Entonces el resultado es "<resultado>"
    Y si el resultado es "rechazado", el sistema muestra el mensaje "<mensaje_error>"

    Ejemplos:
      | fecha_recepcion | fecha_envio  | resultado | mensaje_error                                                        |
      | 2026-01-11      | 2026-01-15   | aceptado  |                                                                     |
      | 2026-01-11      | 2026-01-10   | rechazado | La fecha de envío no puede ser anterior a la recepción de documentos |

  @consulta @detalle
  Escenario: Consultar el detalle de la solicitud
    Cuando el asesor consulta el detalle de la solicitud "SOL-2026-0001"
    Entonces el sistema muestra los siguientes datos:
      | estado_actual               | CREADA     |
      | fecha_creacion              | 2026-01-10 |
      | fecha_ultima_actualizacion  | 2026-01-10 |
      | fechaRecepcionDocs          | (vacío)    |
      | fechaEnvioSolicitud         | (vacío)    |
      | fechaCita                   | (vacío)    |

  @consulta @historial
  Escenario: Consultar historial completo de la solicitud
    Cuando el asesor consulta el historial de la solicitud "SOL-2026-0001"
    Entonces el sistema muestra los cambios de estado en orden cronológico descendente
    Y cada cambio de estado muestra: estado anterior, estado nuevo, usuario, fecha y motivo
    Y el sistema muestra los cambios de fechas en orden cronológico descendente
    Y cada cambio de fecha muestra: campo, valor anterior, valor nuevo, usuario y fecha
