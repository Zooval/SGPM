from behave import *

@step("que el empleado {empleado} se encuentra autenticado en el sistema")
def step_impl(context, empleado):
    context.empleado = empleado


@step("existe un migrante registrado con nombre {nombre} y documento {documento}")
def step_impl(context, nombre, documento):
    context.migrante = {
        "nombre": nombre,
        "documento": documento
    }


@step("el sistema de gestión de citas se encuentra disponible")
def step_impl(context):
    context.citas = []

#               Escenario 1

@step('el empleado reserva una cita para el migrante')
def step_impl(context):
    context.cita_en_proceso = {
        "migrante": context.migrante["nombre"],
        "responsable": context.empleado
    }


@step('ingresa la fecha {fecha} y la hora {hora}')
def step_impl(context, fecha, hora):
    context.fecha = fecha
    context.hora = hora
    context.cita_en_proceso["fecha"] = context.fecha
    context.cita_en_proceso["hora"] = context.hora
    print(context.cita_en_proceso["fecha"])


@step("la cita queda registrada asociada al migrante con la fecha y hora establecida")
def step_impl(context):
    context.citas.append(context.cita_en_proceso)
    context.conflicto = True if context.citas[-1]["migrante"] == context.migrante["nombre"] \
        and context.citas[-1]["responsable"] == context.empleado \
        and context.citas[-1]["fecha"] == context.fecha \
        and context.citas[-1]["hora"] == context.hora \
        else False
    assert len(context.citas) > 0 and context.conflicto is True


@step('la cita tiene como responsable al empleado')
def step_impl(context):
    assert context.cita_en_proceso["responsable"] == context.empleado

#                   Escenario 2

@step('que el empleado tiene una cita registrada el día {fecha} a las {hora}')
def step_impl(context, fecha, hora):
    context.cita_registrada = {
        "fecha": fecha,
        "hora": hora
    }


@step('intenta reservar otra cita para el mismo día {fecha} a las {hora}')
def step_impl(context, fecha, hora):
    context.segunda_cita_registrada = {
        "fecha": fecha,
        "hora": hora
    }



@step("el sistema impide la reserva")
def step_impl(context):
    if context.cita_registrada == context.segunda_cita_registrada:
        print("la fecha u hora elegidas ya estan ocupadas")



@step("solicita seleccionar un horario diferente")
def step_impl(context):
    print("Escoja un horario diferente")

'''
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
'''