import behave.runner
from behave import *

use_step_matcher("re")


@step('que existe un cliente con cédula "0912345678" y correo "cliente@mail\.com"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Dado que existe un cliente con cédula "0912345678" y correo "cliente@mail.com"')


@step('existe una solicitud con código "SOL-2026-0001" para el cliente "0912345678" con fecha de creación "2026-01-10"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Y existe una solicitud con código "SOL-2026-0001" para el cliente "0912345678" con fecha de creación "2026-01-10"')


@step('la solicitud está en estado "Creada"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y la solicitud está en estado "Creada"')


@step('el asesor autenticado es "asesor@agencia\.com"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y el asesor autenticado es "asesor@agencia.com"')


@step('que la transición de "(?P<estado_inicial>.+)" a "(?P<estado_nuevo>.+)" está permitida')
def step_impl(context: behave.runner.Context, estado_inicial: str, estado_nuevo: str):
    """
    :type context: behave.runner.Context
    :type estado_inicial: str
    :type estado_nuevo: str
    """
    raise NotImplementedError(u'STEP: Dado que la transición de "<estado_inicial>" a "<estado_nuevo>" está permitida')


@step('el asesor cambia el estado a "(?P<estado_nuevo>.+)" indicando el motivo "(?P<motivo>.+)"')
def step_impl(context: behave.runner.Context, estado_nuevo: str, motivo: str):
    """
    :type context: behave.runner.Context
    :type estado_nuevo: str
    :type motivo: str
    """
    raise NotImplementedError(
        u'STEP: Cuando el asesor cambia el estado a "<estado_nuevo>" indicando el motivo "<motivo>"')


@step('el asesor visualiza el estado actual como "(?P<estado_nuevo>.+)"')
def step_impl(context: behave.runner.Context, estado_nuevo: str):
    """
    :type context: behave.runner.Context
    :type estado_nuevo: str
    """
    raise NotImplementedError(u'STEP: Entonces el asesor visualiza el estado actual como "<estado_nuevo>"')


@step('el asesor visualiza la "fechaUltimaActualizacion" como "(?P<fecha_evento>.+)"')
def step_impl(context: behave.runner.Context, fecha_evento: str):
    """
    :type context: behave.runner.Context
    :type fecha_evento: str
    """
    raise NotImplementedError(u'STEP: Y el asesor visualiza la "fechaUltimaActualizacion" como "<fecha_evento>"')


@step("al revisar el historial, el asesor visualiza un registro con:")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y al revisar el historial, el asesor visualiza un registro con:
                              | usuario | asesor @ agencia.com |
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


@step('el asesor intenta cambiar el estado a "(?P<estado_nuevo>.+)" indicando el motivo "(?P<motivo>.+)"')
def step_impl(context: behave.runner.Context, estado_nuevo: str, motivo: str):
    """
    :type context: behave.runner.Context
    :type estado_nuevo: str
    :type motivo: str
    """
    raise NotImplementedError(
        u'STEP: Cuando el asesor intenta cambiar el estado a "<estado_nuevo>" indicando el motivo "<motivo>"')


@step('el asesor visualiza el mensaje "(?P<mensaje_error>.+)"')
def step_impl(context: behave.runner.Context, mensaje_error: str):
    """
    :type context: behave.runner.Context
    :type mensaje_error: str
    """
    raise NotImplementedError(u'STEP: Y el asesor visualiza el mensaje "<mensaje_error>"')


@step("al revisar el historial, el asesor no visualiza un registro asociado a esta acción")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Y al revisar el historial, el asesor no visualiza un registro asociado a esta acción')


@step('el asesor visualiza el resultado como "(?P<resultado>.+)"')
def step_impl(context: behave.runner.Context, resultado: str):
    """
    :type context: behave.runner.Context
    :type resultado: str
    """
    raise NotImplementedError(u'STEP: Entonces el asesor visualiza el resultado como "<resultado>"')


@step('si el resultado es "rechazado", el asesor visualiza el mensaje "(?P<mensaje_error>.+)"')
def step_impl(context: behave.runner.Context, mensaje_error: str):
    """
    :type context: behave.runner.Context
    :type mensaje_error: str
    """
    raise NotImplementedError(
        u'STEP: Y si el resultado es "rechazado", el asesor visualiza el mensaje "<mensaje_error>"')


@step('que la solicitud está en estado "Archivada"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Dado que la solicitud está en estado "Archivada"')


@step('que "(?P<tipo_fecha>.+)" es un campo de fecha permitido del proceso')
def step_impl(context: behave.runner.Context, tipo_fecha: str):
    """
    :type context: behave.runner.Context
    :type tipo_fecha: str
    """
    raise NotImplementedError(u'STEP: Dado que "<tipo_fecha>" es un campo de fecha permitido del proceso')


@step('"(?P<fecha_valor>.+)" es igual o posterior a "2026-01-10"')
def step_impl(context: behave.runner.Context, fecha_valor: str):
    """
    :type context: behave.runner.Context
    :type fecha_valor: str
    """
    raise NotImplementedError(u'STEP: Y "<fecha_valor>" es igual o posterior a "2026-01-10"')


@step('el asesor asigna "(?P<tipo_fecha>.+)" con valor "(?P<fecha_valor>.+)"')
def step_impl(context: behave.runner.Context, tipo_fecha: str, fecha_valor: str):
    """
    :type context: behave.runner.Context
    :type tipo_fecha: str
    :type fecha_valor: str
    """
    raise NotImplementedError(u'STEP: Cuando el asesor asigna "<tipo_fecha>" con valor "<fecha_valor>"')


@step('el asesor visualiza "(?P<tipo_fecha>.+)" como "(?P<fecha_valor>.+)"')
def step_impl(context: behave.runner.Context, tipo_fecha: str, fecha_valor: str):
    """
    :type context: behave.runner.Context
    :type tipo_fecha: str
    :type fecha_valor: str
    """
    raise NotImplementedError(u'STEP: Entonces el asesor visualiza "<tipo_fecha>" como "<fecha_valor>"')


@step("al revisar el historial de fechas, el asesor visualiza un registro con:")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y al revisar el historial de fechas, el asesor visualiza un registro con:
                              | usuario | asesor @ agencia.com |
                              | campo | < tipo_fecha > |
          | valorAnterior | < valor_anterior > |
    | valorNuevo | < fecha_valor > |
    | fecha | < fecha_evento > | ')


@step('"(?P<fecha_valor>.+)" es anterior a "2026-01-10"')
def step_impl(context: behave.runner.Context, fecha_valor: str):
    """
    :type context: behave.runner.Context
    :type fecha_valor: str
    """
    raise NotImplementedError(u'STEP: Y "<fecha_valor>" es anterior a "2026-01-10"')


@step('el asesor visualiza que "(?P<tipo_fecha>.+)" mantiene su valor anterior')
def step_impl(context: behave.runner.Context, tipo_fecha: str):
    """
    :type context: behave.runner.Context
    :type tipo_fecha: str
    """
    raise NotImplementedError(u'STEP: Y el asesor visualiza que "<tipo_fecha>" mantiene su valor anterior')


@step('que el asesor visualiza "fechaRecepcionDocs" como "(?P<fecha_recepcion_docs>.+)"')
def step_impl(context: behave.runner.Context, fecha_recepcion_docs: str):
    """
    :type context: behave.runner.Context
    :type fecha_recepcion_docs: str
    """
    raise NotImplementedError(u'STEP: Dado que el asesor visualiza "fechaRecepcionDocs" como "<fecha_recepcion_docs>"')


@step('el asesor consulta el detalle de la solicitud "SOL-2026-0001"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Cuando el asesor consulta el detalle de la solicitud "SOL-2026-0001"')


@step("el asesor visualiza las fechas clave registradas:")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y el asesor visualiza las fechas clave registradas:
                              | fechaCreacion | 2026 - 01 - 10 |
                              | fechaUltimaActualizacion | 2026 - 01 - 10 |
                              | fechaRecepcionDocs | (vacío) |
                              | fechaEnvioSolicitud | (vacío) |
                              | fechaCita | (vacío) | ')


@step('el asesor consulta el historial de la solicitud "SOL-2026-0001"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Cuando el asesor consulta el historial de la solicitud "SOL-2026-0001"')


@step("el asesor visualiza los cambios de estado en orden cronológico descendente")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Entonces el asesor visualiza los cambios de estado en orden cronológico descendente')


@step("cada cambio de estado muestra: estado anterior, estado nuevo, usuario, fecha, motivo")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Y cada cambio de estado muestra: estado anterior, estado nuevo, usuario, fecha, motivo')


@step("el asesor visualiza los cambios de fechas en orden cronológico descendente")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y el asesor visualiza los cambios de fechas en orden cronológico descendente')


@step("cada cambio de fecha muestra: campo, valor anterior, valor nuevo, usuario, fecha")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Y cada cambio de fecha muestra: campo, valor anterior, valor nuevo, usuario, fecha')