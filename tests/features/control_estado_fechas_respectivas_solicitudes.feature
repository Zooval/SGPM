# Created by ximen at 10/1/2026
# language: es

@solicitudes @estado_fechas
Característica: Control de estado y fechas respectivas de las solicitudes
  Como agente de la agencia
  Quiero controlar el estado y las fechas clave de una solicitud
  Para dar seguimiento, evitar inconsistencias y mantener trazabilidad

  Antecedentes:
    Dado que existe un cliente con cédula "<cliente_cedula>" y correo "<cliente_correo>"
    Y existe una solicitud con código "<solicitud_codigo>" para el cliente "<cliente_cedula>" con fecha de creación "<fecha_creacion>"
    Y la solicitud tiene estado "<estado_inicial>"

  @estado @avance_valido
  Esquema del escenario: Avance válido del estado de una solicitud registra historial y fecha
    Dado que la transición de "<estado_inicial>" a "<estado_nuevo>" está permitida
    Cuando el asesor "<asesor_email>" cambia el estado a "<estado_nuevo>" con motivo "<motivo>"
    Entonces la solicitud queda en estado "<estado_nuevo>"
    Y se actualiza la fecha de última actualización a "<fecha_evento>"
    Y se registra un evento en el historial con:
      | usuario  | <asesor_email>   |
      | anterior | <estado_inicial> |
      | nuevo    | <estado_nuevo>   |
      | fecha    | <fecha_evento>   |
      | motivo   | <motivo>         |

    Ejemplos:
      | estado_inicial   | estado_nuevo   | asesor_email   | motivo   | fecha_evento   |
      | <estado_inicial> | <estado_nuevo> | <asesor_email> | <motivo> | <fecha_evento> |

  @estado @avance_invalido
  Esquema del escenario: Prevención de avance inválido del proceso mantiene estado y no registra cambio
    Dado que la transición de "<estado_inicial>" a "<estado_nuevo>" no está permitida
    Cuando el asesor "<asesor_email>" intenta cambiar el estado a "<estado_nuevo>" con motivo "<motivo>"
    Entonces el sistema rechaza el cambio
    Y la solicitud mantiene el estado "<estado_inicial>"
    Y no se registra ningún evento de cambio de estado en el historial
    Y el mensaje de error es "<mensaje_error>"

    Ejemplos:
      | estado_inicial   | estado_nuevo   | asesor_email   | motivo   | mensaje_error   |
      | <estado_inicial> | <estado_nuevo> | <asesor_email> | <motivo> | <mensaje_error> |

  @estado @rechazo_requiere_motivo
  Esquema del escenario: Rechazada exige motivo obligatorio
    Dado que la transición de "<estado_inicial>" a "Rechazada" está permitida
    Cuando el asesor "<asesor_email>" cambia el estado a "Rechazada" con motivo "<motivo>"
    Entonces el resultado del cambio es "<resultado>"
    Y si el resultado es "rechazado" el mensaje de error es "<mensaje_error>"

    Ejemplos:
      | estado_inicial   | asesor_email   | motivo   | resultado   | mensaje_error   |
      | <estado_inicial> | <asesor_email> | <motivo> | <resultado> | <mensaje_error> |

  @estado @archivada_bloquea
  Esquema del escenario: Solicitud archivada no permite cambios de estado ni fechas
    Dado que la solicitud está en estado "Archivada"
    Cuando el asesor "<asesor_email>" intenta cambiar el estado a "<estado_nuevo>" con motivo "<motivo>"
    Entonces el sistema rechaza la modificación
    Y el mensaje de error es "<mensaje_error>"

    Ejemplos:
      | asesor_email   | estado_nuevo   | motivo   | mensaje_error   |
      | <asesor_email> | <estado_nuevo> | <motivo> | <mensaje_error> |

  @fechas @registrar_fecha
  Esquema del escenario: Registrar una fecha clave válida en la solicitud
    Dado que la fecha "<tipo_fecha>" es una fecha permitida del proceso
    Y la fecha "<fecha_valor>" es igual o posterior a "<fecha_creacion>"
    Cuando el asesor "<asesor_email>" asigna "<tipo_fecha>" con valor "<fecha_valor>"
    Entonces la solicitud guarda "<tipo_fecha>" con valor "<fecha_valor>"
    Y se actualiza la fecha de última actualización a "<fecha_evento>"
    Y se registra un evento en el historial de fechas con:
      | usuario       | <asesor_email>   |
      | campo         | <tipo_fecha>     |
      | valorAnterior | <valor_anterior> |
      | valorNuevo    | <fecha_valor>    |
      | fecha         | <fecha_evento>   |

    Ejemplos:
      | fecha_creacion   | tipo_fecha   | valor_anterior   | fecha_valor   | asesor_email   | fecha_evento   |
      | <fecha_creacion> | <tipo_fecha> | <valor_anterior> | <fecha_valor> | <asesor_email> | <fecha_evento> |

  @fechas @fecha_invalida
  Esquema del escenario: Bloquear fecha clave anterior a la fecha de creación
    Dado que la fecha "<tipo_fecha>" es una fecha permitida del proceso
    Y la fecha "<fecha_valor>" es anterior a "<fecha_creacion>"
    Cuando el asesor "<asesor_email>" asigna "<tipo_fecha>" con valor "<fecha_valor>"
    Entonces el sistema rechaza la asignación de fecha
    Y la solicitud no cambia el valor de "<tipo_fecha>"
    Y el mensaje de error es "<mensaje_error>"

    Ejemplos:
      | fecha_creacion   | tipo_fecha   | fecha_valor   | asesor_email   | mensaje_error   |
      | <fecha_creacion> | <tipo_fecha> | <fecha_valor> | <asesor_email> | <mensaje_error> |

  @fechas @coherencia_fechas
  Esquema del escenario: Validar coherencia entre recepción de documentos y envío de solicitud
    Dado que la solicitud tiene "fechaRecepcionDocs" = "<fecha_recepcion_docs>"
    Cuando el asesor "<asesor_email>" asigna "fechaEnvioSolicitud" con valor "<fecha_envio>"
    Entonces el resultado de la asignación es "<resultado>"
    Y si el resultado es "rechazado" el mensaje de error es "<mensaje_error>"

    Ejemplos:
      | fecha_recepcion_docs   | fecha_envio   | asesor_email   | resultado   | mensaje_error   |
      | <fecha_recepcion_docs> | <fecha_envio> | <asesor_email> | <resultado> | <mensaje_error> |

  @consulta @detalle
  Esquema del escenario: Consultar estado actual y fechas asociadas de la solicitud
    Cuando el asesor "<asesor_email>" consulta el detalle de la solicitud "<solicitud_codigo>"
    Entonces se muestra el estado actual "<estado_esperado>"
    Y se muestran las fechas clave registradas:
      | fechaCreacion            | <fecha_creacion> |
      | fechaUltimaActualizacion | <fecha_ultima>   |
      | fechaRecepcionDocs       | <fecha_rec_docs> |
      | fechaEnvioSolicitud      | <fecha_envio>    |
      | fechaCita                | <fecha_cita>     |

    Ejemplos:
      | asesor_email   | solicitud_codigo   | estado_esperado   | fecha_creacion   | fecha_ultima   | fecha_rec_docs   | fecha_envio   | fecha_cita   |
      | <asesor_email> | <solicitud_codigo> | <estado_esperado> | <fecha_creacion> | <fecha_ultima> | <fecha_rec_docs> | <fecha_envio> | <fecha_cita> |

  @consulta @historial
  Esquema del escenario: Revisar historial de estados y fechas de la solicitud
    Cuando el asesor "<asesor_email>" consulta el historial de la solicitud "<solicitud_codigo>"
    Entonces se listan los cambios de estado en orden cronológico descendente
    Y cada cambio incluye: estado anterior, estado nuevo, usuario, fecha, motivo
    Y se listan los cambios de fechas en orden cronológico descendente
    Y cada cambio incluye: campo, valor anterior, valor nuevo, usuario, fecha

    Ejemplos:
      | asesor_email   | solicitud_codigo   |
      | <asesor_email> | <solicitud_codigo> |
