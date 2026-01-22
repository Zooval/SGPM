import behave.runner
from behave import *

use_step_matcher("re")


@step('que existe un cliente con cédula "<cliente_cedula>" y correo "<cliente_correo>"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Dado que existe un cliente con cédula "<cliente_cedula>" y correo "<cliente_correo>"')


@step(
    'existe una solicitud con código "<solicitud_codigo>" para el cliente "<cliente_cedula>" con fecha de creación "<fecha_creacion>"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Y existe una solicitud con código "<solicitud_codigo>" para el cliente "<cliente_cedula>" con fecha de creación "<fecha_creacion>"')


@step('la solicitud tiene estado "<estado_inicial>"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y la solicitud tiene estado "<estado_inicial>"')


@step('que la transición de "(?P<estado_inicial>.+)" a "(?P<estado_nuevo>.+)" está permitida')
def step_impl(context: behave.runner.Context, estado_inicial: str, estado_nuevo: str):
    """
    :type context: behave.runner.Context
    :type estado_inicial: str
    :type estado_nuevo: str
    """
    raise NotImplementedError(u'STEP: Dado que la transición de "<estado_inicial>" a "<estado_nuevo>" está permitida')


@step('el asesor "(?P<asesor_email>.+)" cambia el estado a "(?P<estado_nuevo>.+)" con motivo "(?P<motivo>.+)"')
def step_impl(context: behave.runner.Context, asesor_email: str, estado_nuevo: str, motivo: str):
    """
    :type context: behave.runner.Context
    :type asesor_email: str
    :type estado_nuevo: str
    :type motivo: str
    """
    raise NotImplementedError(
        u'STEP: Cuando el asesor "<asesor_email>" cambia el estado a "<estado_nuevo>" con motivo "<motivo>"')


@step('la solicitud queda en estado "(?P<estado_nuevo>.+)"')
def step_impl(context: behave.runner.Context, estado_nuevo: str):
    """
    :type context: behave.runner.Context
    :type estado_nuevo: str
    """
    raise NotImplementedError(u'STEP: Entonces la solicitud queda en estado "<estado_nuevo>"')


@step('se actualiza la fecha de última actualización a "(?P<fecha_evento>.+)"')
def step_impl(context: behave.runner.Context, fecha_evento: str):
    """
    :type context: behave.runner.Context
    :type fecha_evento: str
    """
    raise NotImplementedError(u'STEP: Y se actualiza la fecha de última actualización a "<fecha_evento>"')


@step("se registra un evento en el historial con:")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y se registra un evento en el historial con:
                              | usuario | < asesor_email > |
          | anterior | < estado_inicial > |
    | nuevo | < estado_nuevo > |
    | fecha | < fecha_evento > |
    | motivo | < motivo > | ')


@step('que la transición de "(?P<estado_inicial>.+)" a "(?P<estado_nuevo>.+)" no está permitida')
def step_impl(context: behave.runner.Context, estado_inicial: str, estado_nuevo: str):
    """
    :type context: behave.runner.Context
    :type estado_inicial: str
    :type estado_nuevo: str
    """
    raise NotImplementedError(
        u'STEP: Dado que la transición de "<estado_inicial>" a "<estado_nuevo>" no está permitida')


@step('el asesor "(?P<asesor_email>.+)" intenta cambiar el estado a "(?P<estado_nuevo>.+)" con motivo "(?P<motivo>.+)"')
def step_impl(context: behave.runner.Context, asesor_email: str, estado_nuevo: str, motivo: str):
    """
    :type context: behave.runner.Context
    :type asesor_email: str
    :type estado_nuevo: str
    :type motivo: str
    """
    raise NotImplementedError(
        u'STEP: Cuando el asesor "<asesor_email>" intenta cambiar el estado a "<estado_nuevo>" con motivo "<motivo>"')


@step("el sistema rechaza el cambio")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces el sistema rechaza el cambio')


@step('la solicitud mantiene el estado "(?P<estado_inicial>.+)"')
def step_impl(context: behave.runner.Context, estado_inicial: str):
    """
    :type context: behave.runner.Context
    :type estado_inicial: str
    """
    raise NotImplementedError(u'STEP: Y la solicitud mantiene el estado "<estado_inicial>"')


@step("no se registra ningún evento de cambio de estado en el historial")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y no se registra ningún evento de cambio de estado en el historial')


@step('el mensaje de error es "(?P<mensaje_error>.+)"')
def step_impl(context: behave.runner.Context, mensaje_error: str):
    """
    :type context: behave.runner.Context
    :type mensaje_error: str
    """
    raise NotImplementedError(u'STEP: Y el mensaje de error es "<mensaje_error>"')


@step('el resultado del cambio es "(?P<resultado>.+)"')
def step_impl(context: behave.runner.Context, resultado: str):
    """
    :type context: behave.runner.Context
    :type resultado: str
    """
    raise NotImplementedError(u'STEP: Entonces el resultado del cambio es "<resultado>"')


@step('si el resultado es "rechazado" el mensaje de error es "(?P<mensaje_error>.+)"')
def step_impl(context: behave.runner.Context, mensaje_error: str):
    """
    :type context: behave.runner.Context
    :type mensaje_error: str
    """
    raise NotImplementedError(u'STEP: Y si el resultado es "rechazado" el mensaje de error es "<mensaje_error>"')


@step('que la solicitud está en estado "Archivada"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Dado que la solicitud está en estado "Archivada"')


@step("el sistema rechaza la modificación")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces el sistema rechaza la modificación')


@step('que la fecha "(?P<tipo_fecha>.+)" es una fecha permitida del proceso')
def step_impl(context: behave.runner.Context, tipo_fecha: str):
    """
    :type context: behave.runner.Context
    :type tipo_fecha: str
    """
    raise NotImplementedError(u'STEP: Dado que la fecha "<tipo_fecha>" es una fecha permitida del proceso')


@step('la fecha "(?P<fecha_valor>.+)" es igual o posterior a "(?P<fecha_creacion>.+)"')
def step_impl(context: behave.runner.Context, fecha_valor: str, fecha_creacion: str):
    """
    :type context: behave.runner.Context
    :type fecha_valor: str
    :type fecha_creacion: str
    """
    raise NotImplementedError(u'STEP: Y la fecha "<fecha_valor>" es igual o posterior a "<fecha_creacion>"')


@step('el asesor "(?P<asesor_email>.+)" asigna "(?P<tipo_fecha>.+)" con valor "(?P<fecha_valor>.+)"')
def step_impl(context: behave.runner.Context, asesor_email: str, tipo_fecha: str, fecha_valor: str):
    """
    :type context: behave.runner.Context
    :type asesor_email: str
    :type tipo_fecha: str
    :type fecha_valor: str
    """
    raise NotImplementedError(
        u'STEP: Cuando el asesor "<asesor_email>" asigna "<tipo_fecha>" con valor "<fecha_valor>"')


@step('la solicitud guarda "(?P<tipo_fecha>.+)" con valor "(?P<fecha_valor>.+)"')
def step_impl(context: behave.runner.Context, tipo_fecha: str, fecha_valor: str):
    """
    :type context: behave.runner.Context
    :type tipo_fecha: str
    :type fecha_valor: str
    """
    raise NotImplementedError(u'STEP: Entonces la solicitud guarda "<tipo_fecha>" con valor "<fecha_valor>"')


@step("se registra un evento en el historial de fechas con:")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y se registra un evento en el historial de fechas con:
                              | usuario | < asesor_email > |
          | campo | < tipo_fecha > |
    | valorAnterior | < valor_anterior > |
    | valorNuevo | < fecha_valor > |
    | fecha | < fecha_evento > | ')


@step('la fecha "(?P<fecha_valor>.+)" es anterior a "(?P<fecha_creacion>.+)"')
def step_impl(context: behave.runner.Context, fecha_valor: str, fecha_creacion: str):
    """
    :type context: behave.runner.Context
    :type fecha_valor: str
    :type fecha_creacion: str
    """
    raise NotImplementedError(u'STEP: Y la fecha "<fecha_valor>" es anterior a "<fecha_creacion>"')


@step("el sistema rechaza la asignación de fecha")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces el sistema rechaza la asignación de fecha')


@step('la solicitud no cambia el valor de "(?P<tipo_fecha>.+)"')
def step_impl(context: behave.runner.Context, tipo_fecha: str):
    """
    :type context: behave.runner.Context
    :type tipo_fecha: str
    """
    raise NotImplementedError(u'STEP: Y la solicitud no cambia el valor de "<tipo_fecha>"')


@step('que la solicitud tiene "fechaRecepcionDocs" = "(?P<fecha_recepcion_docs>.+)"')
def step_impl(context: behave.runner.Context, fecha_recepcion_docs: str):
    """
    :type context: behave.runner.Context
    :type fecha_recepcion_docs: str
    """
    raise NotImplementedError(u'STEP: Dado que la solicitud tiene "fechaRecepcionDocs" = "<fecha_recepcion_docs>"')


@step('el resultado de la asignación es "(?P<resultado>.+)"')
def step_impl(context: behave.runner.Context, resultado: str):
    """
    :type context: behave.runner.Context
    :type resultado: str
    """
    raise NotImplementedError(u'STEP: Entonces el resultado de la asignación es "<resultado>"')


@step('el asesor "(?P<asesor_email>.+)" consulta el detalle de la solicitud "(?P<solicitud_codigo>.+)"')
def step_impl(context: behave.runner.Context, asesor_email: str, solicitud_codigo: str):
    """
    :type context: behave.runner.Context
    :type asesor_email: str
    :type solicitud_codigo: str
    """
    raise NotImplementedError(
        u'STEP: Cuando el asesor "<asesor_email>" consulta el detalle de la solicitud "<solicitud_codigo>"')


@step('se muestra el estado actual "(?P<estado_esperado>.+)"')
def step_impl(context: behave.runner.Context, estado_esperado: str):
    """
    :type context: behave.runner.Context
    :type estado_esperado: str
    """
    raise NotImplementedError(u'STEP: Entonces se muestra el estado actual "<estado_esperado>"')


@step("se muestran las fechas clave registradas:")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y se muestran las fechas clave registradas:
                              | fechaCreacion | < fecha_creacion > |
          | fechaUltimaActualizacion | < fecha_ultima > |
    | fechaRecepcionDocs | < fecha_rec_docs > |
    | fechaEnvioSolicitud | < fecha_envio > |
    | fechaCita | < fecha_cita > | ')


@step('el asesor "(?P<asesor_email>.+)" consulta el historial de la solicitud "(?P<solicitud_codigo>.+)"')
def step_impl(context: behave.runner.Context, asesor_email: str, solicitud_codigo: str):
    """
    :type context: behave.runner.Context
    :type asesor_email: str
    :type solicitud_codigo: str
    """
    raise NotImplementedError(
        u'STEP: Cuando el asesor "<asesor_email>" consulta el historial de la solicitud "<solicitud_codigo>"')


@step("se listan los cambios de estado en orden cronológico descendente")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces se listan los cambios de estado en orden cronológico descendente')


@step("cada cambio incluye: estado anterior, estado nuevo, usuario, fecha, motivo")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y cada cambio incluye: estado anterior, estado nuevo, usuario, fecha, motivo')


@step("se listan los cambios de fechas en orden cronológico descendente")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y se listan los cambios de fechas en orden cronológico descendente')


@step("cada cambio incluye: campo, valor anterior, valor nuevo, usuario, fecha")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y cada cambio incluye: campo, valor anterior, valor nuevo, usuario, fecha')