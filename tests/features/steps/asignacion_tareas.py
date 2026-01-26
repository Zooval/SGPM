from behave import step
from datetime import datetime
from SGPM.domain.entities import Asesor, Tarea, Notificacion
from SGPM.domain.enums import RolUsuario, EstadoTarea, PrioridadTarea, TipoNotificacion


def _init_context(context):
    if not hasattr(context, "supervisor"):
        context.supervisor = None
    if not hasattr(context, "asesores"):
        context.asesores = {}
    if not hasattr(context, "tareas"):
        context.tareas = {}
    if not hasattr(context, "notificaciones"):
        context.notificaciones = []
    if not hasattr(context, "recordatorios"):
        context.recordatorios = []


def _parse_prioridad(prioridad_texto: str) -> PrioridadTarea:
    mapeo = {
        "baja": PrioridadTarea.BAJA,
        "media": PrioridadTarea.MEDIA,
        "alta": PrioridadTarea.ALTA,
        "critica": PrioridadTarea.CRITICA,
    }
    return mapeo.get(prioridad_texto.lower(), PrioridadTarea.MEDIA)


def _parse_estado(estado_texto: str) -> EstadoTarea:
    mapeo = {
        "pendiente": EstadoTarea.PENDIENTE,
        "en progreso": EstadoTarea.EN_PROGRESO,
        "completada": EstadoTarea.COMPLETADA,
        "cancelada": EstadoTarea.CANCELADA,
        "asignada": EstadoTarea.PENDIENTE,
    }
    return mapeo.get(estado_texto.lower(), EstadoTarea.PENDIENTE)


# ======================================================
# DADOS
# ======================================================

@step('que existe un supervisor autenticado con correo "{correo}"')
def step_impl(context, correo):
    _init_context(context)
    context.supervisor = Asesor("Supervisor", "Sistema", correo, RolUsuario.ADMIN)


@step('existe un asesor con identificador "{id_asesor}" y correo "{correo}"')
def step_impl(context, id_asesor, correo):
    _init_context(context)
    context.asesores[id_asesor] = Asesor("Asesor", "Test", correo, RolUsuario.ASESOR)

@step('existe una tarea con código "{codigo}" y prioridad "{prioridad}"')
def step_impl(context, codigo, prioridad):
    _init_context(context)
    context.tareas[codigo] = Tarea(codigo, f"Tarea {codigo}", _parse_prioridad(prioridad))


@step('que existe una tarea con código "{codigo}" y prioridad "{prioridad}"')
def step_impl(context, codigo, prioridad):
    _init_context(context)
    context.tareas[codigo] = Tarea(codigo, f"Tarea {codigo}", _parse_prioridad(prioridad))


@step('que el asesor "{id_asesor}" tiene tareas previamente asignadas')
def step_impl(context, id_asesor):
    _init_context(context)
    asesor = context.asesores.get(id_asesor)
    for row in context.table:
        codigo = row["codigo"].strip()
        tarea = Tarea(codigo, f"Tarea {codigo}", PrioridadTarea.MEDIA)
        tarea.asignar_a_asesor(asesor)
        context.tareas[codigo] = tarea



@step('que la tarea "{codigo}" está asignada al asesor "{id_asesor}" sin fecha')
def step_impl(context, codigo, id_asesor):
    _init_context(context)
    asesor = context.asesores.get(id_asesor)
    if codigo in context.tareas:
        tarea = context.tareas[codigo]
    else:
        tarea = Tarea(codigo, f"Tarea {codigo}", PrioridadTarea.MEDIA)
        context.tareas[codigo] = tarea
    tarea.asignar_a_asesor(asesor)


@step('que la tarea "{codigo}" está asignada al asesor "{id_asesor}"')
def step_impl(context, codigo, id_asesor):
    _init_context(context)
    asesor = context.asesores.get(id_asesor)
    if codigo in context.tareas:
        tarea = context.tareas[codigo]
    else:
        tarea = Tarea(codigo, f"Tarea {codigo}", PrioridadTarea.MEDIA)
        context.tareas[codigo] = tarea
    tarea.asignar_a_asesor(asesor)


@step('que la tarea "{codigo}" tiene asignado el asesor "{id_asesor}" y vence el "{fecha}"')
def step_impl(context, codigo, id_asesor, fecha):
    _init_context(context)
    asesor = context.asesores.get(id_asesor)
    fecha_vencimiento = datetime.strptime(fecha, "%Y-%m-%d")
    tarea = Tarea(codigo, f"Tarea {codigo}", PrioridadTarea.MEDIA, vencimiento=fecha_vencimiento)
    tarea.asignar_a_asesor(asesor)
    context.tareas[codigo] = tarea


# ======================================================
# CUANDO
# ======================================================

@step('el supervisor asigna la tarea "{codigo}" al asesor "{id_asesor}"')
def step_impl(context, codigo, id_asesor):
    tarea = context.tareas.get(codigo)
    asesor = context.asesores.get(id_asesor)
    tarea.asignar_a_asesor(asesor)


@step('el supervisor programa la tarea "{codigo}" al asesor "{id_asesor}" con fecha de vencimiento "{fecha}"')
def step_impl(context, codigo, id_asesor, fecha):
    tarea = context.tareas.get(codigo)
    asesor = context.asesores.get(id_asesor)
    fecha_vencimiento = datetime.strptime(fecha, "%Y-%m-%d")
    tarea.establecer_vencimiento(fecha_vencimiento)
    tarea.asignar_a_asesor(asesor)


@step("el proceso de asignación finaliza")
def step_impl(context):
    tarea = context.tareas.get("TAR-006")
    if tarea and tarea.asignadaA:
        notif = Notificacion.crear_notificacion_asignacion_tarea(
            f"NOT-{tarea.idTarea}", tarea.asignadaA, tarea
        )
        context.notificaciones.append(notif)


@step("se alcanza 24 horas antes de la fecha de vencimiento")
def step_impl(context):
    tarea = context.tareas.get("TAR-007")
    if tarea and tarea.asignadaA:
        recordatorio = Notificacion.crear_recordatorio_vencimiento(
            f"REC-{tarea.idTarea}", tarea.asignadaA, tarea
        )
        context.recordatorios.append(recordatorio)


@step('el asesor cambia el estado de la tarea a "{nuevo_estado}"')
def step_impl(context, nuevo_estado):
    tarea = context.tareas.get("TAR-008")
    estado_enum = _parse_estado(nuevo_estado)
    tarea.cambiar_estado(estado_enum)


@step('el supervisor actualiza la prioridad de la tarea a "{nueva_prioridad}"')
def step_impl(context, nueva_prioridad):
    tarea = context.tareas.get("TAR-009")
    prioridad_enum = _parse_prioridad(nueva_prioridad)
    tarea.actualizar_prioridad(prioridad_enum)


# ======================================================
# ENTONCES
# ======================================================


@step('la tarea "{codigo}" queda asignada al asesor "{id_asesor}"')
def step_impl(context, codigo, id_asesor):
    tarea = context.tareas.get(codigo)
    asesor = context.asesores.get(id_asesor)
    assert tarea is not None, f"La tarea {codigo} no existe en el contexto"
    assert asesor is not None, f"El asesor {id_asesor} no existe en el contexto"
    assert tarea.esta_asignada(), f"La tarea {codigo} no está asignada"
    assert tarea.asignadaA == asesor, f"La tarea no está asignada al asesor correcto"


@step('la tarea tiene estado "{estado}"')
def step_impl(context, estado):
    tarea = context.tareas.get("TAR-001")
    if estado.lower() == "asignada":
        assert tarea.esta_asignada(), "La tarea no está asignada"
    else:
        estado_enum = _parse_estado(estado)
        assert tarea.estado == estado_enum


@step('el asesor "{id_asesor}" mantiene sus tareas anteriores')
def step_impl(context, id_asesor):
    asesor = context.asesores.get(id_asesor)
    assert len(asesor.obtener_tareas()) >= 2


@step('el asesor "{id_asesor}" tiene asignada la tarea "{codigo}"')
def step_impl(context, id_asesor, codigo):
    asesor = context.asesores.get(id_asesor)
    assert asesor.tiene_tarea(codigo), f"El asesor no tiene la tarea {codigo}"


@step('la tarea "{codigo}" registra la fecha de vencimiento "{fecha}"')
def step_impl(context, codigo, fecha):
    tarea = context.tareas.get(codigo)
    fecha_esperada = datetime.strptime(fecha, "%Y-%m-%d")
    assert tarea.vencimiento is not None
    assert tarea.vencimiento.date() == fecha_esperada.date()


@step('el asesor "{id_asesor}" recibe una notificación de nueva tarea')
def step_impl(context, id_asesor):
    asesor = context.asesores.get(id_asesor)
    notifs = [n for n in context.notificaciones if n.obtener_destinatario() == asesor.emailAsesor]
    assert len(notifs) > 0
    assert any(n.obtener_tipo() == TipoNotificacion.ASIGNACION_TAREA for n in notifs)


@step('el sistema envía un recordatorio al asesor "{id_asesor}"')
def step_impl(context, id_asesor):
    asesor = context.asesores.get(id_asesor)
    recs = [r for r in context.recordatorios if r.obtener_destinatario() == asesor.emailAsesor]
    assert len(recs) > 0
    assert any(r.obtener_tipo() == TipoNotificacion.RECORDATORIO for r in recs)


@step('la tarea "{codigo}" queda en estado "{estado}"')
def step_impl(context, codigo, estado):
    tarea = context.tareas.get(codigo)
    estado_enum = _parse_estado(estado)
    assert tarea.estado == estado_enum


@step('la tarea "{codigo}" refleja la prioridad "{prioridad}"')
def step_impl(context, codigo, prioridad):
    tarea = context.tareas.get(codigo)
    prioridad_enum = _parse_prioridad(prioridad)
    assert tarea.prioridad == prioridad_enum

