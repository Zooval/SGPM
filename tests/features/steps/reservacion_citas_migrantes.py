from behave import *

@step("que el empleado {nombre_empleado} se encuentra autenticado en el sistema")
def step_impl(context, nombre_empleado):
    context.empleado = empleado


@step('existe un migrante registrado con nombre {migrante_registrado} y documento {documento}}')
def step_impl(context, migrante_registrado, documento):
    context.migrante = {
        "nombre": nombre,
        "documento": documento
    }


@step("el sistema de gestión de citas se encuentra disponible")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y el sistema de gestión de citas se encuentra disponible')


@step('el empleado reserva una cita para el migrante "María López"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Cuando el empleado reserva una cita para el migrante "María López"')


@step('ingresa la fecha "19-04-2025" y la hora "10:00"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y ingresa la fecha "19-04-2025" y la hora "10:00"')


@step("la cita queda registrada asociada al migrante")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces la cita queda registrada asociada al migrante')


@step('la cita tiene como responsable al empleado "Juan Pérez"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y la cita tiene como responsable al empleado "Juan Pérez"')


@step('que el empleado tiene una cita registrada el día "19-04-2025" a las "10:00"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Dado que el empleado tiene una cita registrada el día "19-04-2025" a las "10:00"')


@step('intenta reservar otra cita para el mismo día "19-04-2025" a las "10:00"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Cuando intenta reservar otra cita para el mismo día "19-04-2025" a las "10:00"')


@step("el sistema impide la reserva")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces el sistema impide la reserva')


@step("solicita seleccionar un horario diferente")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y solicita seleccionar un horario diferente')


@step('que existe una cita registrada para el migrante "María López"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Dado que existe una cita registrada para el migrante "María López"')


@step('el empleado consulta la agenda del día "19-04-2025"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Cuando el empleado consulta la agenda del día "19-04-2025"')


@step('la cita se muestra a las "10:00" asociada al migrante "María López"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces la cita se muestra a las "10:00" asociada al migrante "María López"')


@step('que existe una cita registrada el día "19-04-2025" a las "10:00"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Dado que existe una cita registrada el día "19-04-2025" a las "10:00"')


@step('el empleado modifica la cita a la fecha "20-04-2025" y hora "11:30"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Cuando el empleado modifica la cita a la fecha "20-04-2025" y hora "11:30"')


@step("la cita se actualiza correctamente")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces la cita se actualiza correctamente')


@step("el cambio queda registrado en el historial de la cita")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y el cambio queda registrado en el historial de la cita')


@step('que existe una cita registrada para el día "20-04-2025" a las "11:30"')
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Dado que existe una cita registrada para el día "20-04-2025" a las "11:30"')


@step("el empleado cancela la cita")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Cuando el empleado cancela la cita')


@step("la cita deja de estar activa")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Entonces la cita deja de estar activa')


@step("la cancelación queda registrada en el sistema")
def step_impl(context: behave.runner.Context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: Y la cancelación queda registrada en el sistema')