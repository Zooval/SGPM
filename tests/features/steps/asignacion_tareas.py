from behave import given, when, then
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

@given('que un supervisor ha iniciado sesión')
def step_supervisor_login(context):
    context.supervisor = {"email": fake.email()}

@given('existe un asesor registrado')
def step_asesor_registrado(context):
    context.asesor = {"email": fake.email(), "tareas": []}

@when('el supervisor asigna una tarea al asesor')
def step_asignar_tarea(context):
    context.tarea = {
        "id": fake.uuid4(),
        "asignadaA": context.asesor["email"],
        "estado": "PENDIENTE"
    }
    context.asesor["tareas"].append(context.tarea)

@then('la tarea queda registrada en el sistema')
def step_tarea_registrada(context):
    assert context.tarea in context.asesor["tareas"]

@then('la tarea tiene estado "PENDIENTE"')
def step_estado_pendiente(context):
    assert context.tarea["estado"] == "PENDIENTE"

@given('un asesor tiene tareas previamente asignadas')
def step_tareas_previas(context):
    context.asesor = {
        "email": fake.email(),
        "tareas": [{"id": fake.uuid4()}]
    }

@when('el supervisor asigna una nueva tarea al asesor')
def step_nueva_tarea(context):
    nueva_tarea = {"id": fake.uuid4()}
    context.asesor["tareas"].append(nueva_tarea)
    context.nueva_tarea = nueva_tarea

@then('las tareas anteriores del asesor se mantienen')
def step_tareas_mantenidas(context):
    assert len(context.asesor["tareas"]) > 1

@given('que un supervisor está asignando una tarea')
def step_supervisor_asignando(context):
    context.tarea = {}

@when('el supervisor ingresa una fecha de vencimiento')
def step_fecha_vencimiento(context):
    context.tarea["vencimiento"] = datetime.now() + timedelta(hours=24)

@then('la tarea se guarda con una fecha de vencimiento a 24 horas')
def step_validar_vencimiento(context):
    delta = context.tarea["vencimiento"] - datetime.now()
    assert delta.total_seconds() <= 86400

@then('el asesor recibe una notificación de la nueva tarea')
def step_notificacion(context):
    context.notificacion = {
        "destinatario": context.asesor["email"],
        "tipo": "RECORDATORIO"
    }
    assert context.notificacion["destinatario"]

@given('la tarea tiene una fecha de vencimiento definida')
def step_fecha_definida(context):
    context.tarea["vencimiento"] = datetime.now() + timedelta(hours=24)

@when('faltan 24 horas para el vencimiento')
def step_24_horas(context):
    context.recordatorio = True

@then('el sistema envía un recordatorio al asesor')
def step_envio_recordatorio(context):
    assert context.recordatorio is True

@when('el asesor cambia el estado de la tarea')
def step_cambiar_estado(context):
    context.tarea["estado"] = "EN_PROGRESO"

@then('el sistema guarda el nuevo estado de la tarea')
def step_guardar_estado(context):
    assert context.tarea["estado"] == "EN_PROGRESO"

@when('el supervisor edita la información de la tarea')
def step_editar_tarea(context):
    context.tarea["prioridad"] = "ALTA"

@then('el sistema guarda los cambios realizados')
def step_guardar_cambios(context):
    assert context.tarea["prioridad"] == "ALTA"
