# Created by ximen at 10/1/2026
# language: es

@solicitudes @estado_fechas
Característica: Control de estado y fechas clave de una solicitud
  Como asesor
  Quiero actualizar el estado y registrar fechas clave de una solicitud
  Para dar seguimiento, evitar inconsistencias y mantener trazabilidad

  Antecedentes:
    Dado que existe un cliente con cédula "0912345678" y correo "cliente@mail.com"
    Y existe una solicitud con código "SOL-2026-0001" para el cliente "0912345678" con fecha de creación "2026-01-10"
    Y la solicitud está en estado "Creada"
    Y el asesor autenticado es "asesor@agencia.com"

  @estado @avance_valido
  Esquema del escenario: Cambiar a un estado permitido registra el cambio y actualiza la fecha
    Dado que la transición de "<estado_inicial>" a "<estado_nuevo>" está permitida
    Y la solicitud está en estado "<estado_inicial>"
    Cuando el asesor cambia el estado a "<estado_nuevo>" indicando el motivo "<motivo>"
    Entonces el asesor visualiza el estado actual como "<estado_nuevo>"
    Y el asesor visualiza la "fechaUltimaActualizacion" como "<fecha_evento>"
    Y al revisar el historial, el asesor visualiza un registro con:
      | usuario  | asesor@agencia.com |
      | anterior | <estado_inicial>   |
      | nuevo    | <estado_nuevo>     |
      | fecha    | <fecha_evento>     |
      | motivo   | <motivo>           |

    Ejemplos:
      | estado_inicial | estado_nuevo  | motivo                 | fecha_evento |
      | Creada         | En revisión   | Verificación inicial   | 2026-01-12   |
      | En revisión    | Enviada       | Documentos completos   | 2026-01-15   |
      | Enviada        | Aprobada      | Respuesta favorable    | 2026-01-20   |

  @estado @avance_invalido
  Esquema del escenario: Evitar una transición no permitida mantiene el estado y muestra el motivo
    Dado que la transición de "<estado_inicial>" a "<estado_nuevo>" no está permitida
    Y la solicitud está en estado "<estado_inicial>"
    Cuando el asesor intenta cambiar el estado a "<estado_nuevo>" indicando el motivo "<motivo>"
    Entonces el asesor visualiza el estado actual como "<estado_inicial>"
    Y el asesor visualiza el mensaje "<mensaje_error>"
    Y al revisar el historial, el asesor no visualiza un registro asociado a esta acción

    Ejemplos:
      | estado_inicial | estado_nuevo | motivo              | mensaje_error                          |
      | Creada         | Aprobada     | Saltar revisión     | No se permite la transición solicitada |
      | Aprobada       | En revisión  | Reabrir análisis    | No se permite la transición solicitada |

  @estado @rechazo_requiere_motivo
  Esquema del escenario: Rechazar exige motivo obligatorio
    Dado que la transición de "<estado_inicial>" a "Rechazada" está permitida
    Y la solicitud está en estado "<estado_inicial>"
    Cuando el asesor cambia el estado a "Rechazada" indicando el motivo "<motivo>"
    Entonces el asesor visualiza el resultado como "<resultado>"
    Y si el resultado es "rechazado", el asesor visualiza el mensaje "<mensaje_error>"

    Ejemplos:
      | estado_inicial | motivo                       | resultado | mensaje_error                          |
      | En revisión    | Documentación incompleta     | aceptado  |                                       |
      | En revisión    |                             | rechazado | El motivo es obligatorio al rechazar  |

  @estado @archivada_bloquea
  Esquema del escenario: Una solicitud archivada no permite cambios
    Dado que la solicitud está en estado "Archivada"
    Cuando el asesor intenta cambiar el estado a "<estado_nuevo>" indicando el motivo "<motivo>"
    Entonces el asesor visualiza el estado actual como "Archivada"
    Y el asesor visualiza el mensaje "<mensaje_error>"
    Y al revisar el historial, el asesor no visualiza un registro asociado a esta acción

    Ejemplos:
      | estado_nuevo | motivo          | mensaje_error                       |
      | En revisión  | Retomar trámite | No se permiten cambios en Archivada |
      | Rechazada    | Cerrar trámite  | No se permiten cambios en Archivada |

  @fechas @registrar_fecha
  Esquema del escenario: Registrar una fecha clave válida actualiza la solicitud y queda en el historial de fechas
    Dado que "<tipo_fecha>" es un campo de fecha permitido del proceso
    Y "<fecha_valor>" es igual o posterior a "2026-01-10"
    Cuando el asesor asigna "<tipo_fecha>" con valor "<fecha_valor>"
    Entonces el asesor visualiza "<tipo_fecha>" como "<fecha_valor>"
    Y el asesor visualiza la "fechaUltimaActualizacion" como "<fecha_evento>"
    Y al revisar el historial de fechas, el asesor visualiza un registro con:
      | usuario       | asesor@agencia.com |
      | campo         | <tipo_fecha>       |
      | valorAnterior | <valor_anterior>   |
      | valorNuevo    | <fecha_valor>      |
      | fecha         | <fecha_evento>     |

    Ejemplos:
      | tipo_fecha          | valor_anterior | fecha_valor  | fecha_evento |
      | fechaRecepcionDocs  | (vacío)        | 2026-01-11    | 2026-01-11   |
      | fechaEnvioSolicitud | (vacío)        | 2026-01-15    | 2026-01-15   |
      | fechaCita           | (vacío)        | 2026-01-18    | 2026-01-16   |

  @fechas @fecha_invalida
  Esquema del escenario: Bloquear una fecha anterior a la creación muestra el error y no cambia el valor
    Dado que "<tipo_fecha>" es un campo de fecha permitido del proceso
    Y "<fecha_valor>" es anterior a "2026-01-10"
    Cuando el asesor asigna "<tipo_fecha>" con valor "<fecha_valor>"
    Entonces el asesor visualiza el mensaje "<mensaje_error>"
    Y el asesor visualiza que "<tipo_fecha>" mantiene su valor anterior

    Ejemplos:
      | tipo_fecha         | fecha_valor  | mensaje_error                                           |
      | fechaRecepcionDocs | 2026-01-05   | La fecha no puede ser anterior a la fecha de creación   |
      | fechaCita          | 2026-01-01   | La fecha no puede ser anterior a la fecha de creación   |

  @fechas @coherencia_fechas
  Esquema del escenario: No permitir que el envío sea anterior a la recepción de documentos
    Dado que el asesor visualiza "fechaRecepcionDocs" como "<fecha_recepcion_docs>"
    Cuando el asesor asigna "fechaEnvioSolicitud" con valor "<fecha_envio>"
    Entonces el asesor visualiza el resultado como "<resultado>"
    Y si el resultado es "rechazado", el asesor visualiza el mensaje "<mensaje_error>"

    Ejemplos:
      | fecha_recepcion_docs | fecha_envio  | resultado | mensaje_error                                                        |
      | 2026-01-11           | 2026-01-15   | aceptado  |                                                                     |
      | 2026-01-11           | 2026-01-10   | rechazado | La fecha de envío no puede ser anterior a la recepción de documentos |

  @consulta @detalle
  Escenario: Consultar el detalle muestra el estado y las fechas registradas
    Cuando el asesor consulta el detalle de la solicitud "SOL-2026-0001"
    Entonces el asesor visualiza el estado actual como "Creada"
    Y el asesor visualiza las fechas clave registradas:
      | fechaCreacion            | 2026-01-10 |
      | fechaUltimaActualizacion | 2026-01-10 |
      | fechaRecepcionDocs       | (vacío)    |
      | fechaEnvioSolicitud      | (vacío)    |
      | fechaCita                | (vacío)    |

  @consulta @historial
  Escenario: Consultar el historial muestra cambios de estado y fechas en orden reciente
    Cuando el asesor consulta el historial de la solicitud "SOL-2026-0001"
    Entonces el asesor visualiza los cambios de estado en orden cronológico descendente
    Y cada cambio de estado muestra: estado anterior, estado nuevo, usuario, fecha, motivo
    Y el asesor visualiza los cambios de fechas en orden cronológico descendente
    Y cada cambio de fecha muestra: campo, valor anterior, valor nuevo, usuario, fecha

