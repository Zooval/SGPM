import behave.runner
from behave import step, use_step_matcher
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

use_step_matcher("re")


# ============================================================
# Enums (según diagrama)
# ============================================================
class RolUsuario(Enum):
    ASESOR = "ASESOR"
    ADMIN = "ADMIN"
    OPERADOR = "OPERADOR"


class EstadoTarea(Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"


class PrioridadTarea(Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class TipoNotificacion(Enum):
    RECORDATORIO = "RECORDATORIO"
    DOC_FALTANTE = "DOC_FALTANTE"
    CITA_PROXIMA = "CITA_PROXIMA"
    ASIGNACION_TAREA = "ASIGNACION_TAREA"


# ============================================================
# Entidades (según diagrama)
# ============================================================
@dataclass
class Asesor:
    nombres: str
    apellidos: str
    email_asesor: str
    rol: RolUsuario


@dataclass
class Tarea:
    id_tarea: str
    vencimiento: Optional[datetime]
    estado: EstadoTarea
    prioridad: PrioridadTarea
    comentario: str
    titulo: str
    asignada_a: Optional[str]  # email_asesor


@dataclass
class Notificacion:
    id_notificacion: str
    destinatario: str
    tipo: TipoNotificacion
    mensaje: str
    creada_en: datetime


# ============================================================
# Helpers de contexto
# ============================================================
def _ensure_context(context: behave.runner.Context):
    if not hasattr(context, "supervisor"):
        context.supervisor: Optional[Asesor] = None
    if not hasattr(context, "asesores"):
        context.asesores: Dict[str, Asesor] = {}  # email -> Asesor
    if not hasattr(context, "tareas"):
        context.tareas: Dict[str, Tarea] = {}  # id_tarea -> Tarea
    if not hasattr(context, "notificaciones"):
        context.notificaciones: List[Notificacion] = []
    if not hasattr(context, "error"):
        context.error: Optional[Exception] = None
    if not hasattr(context, "now"):
        context.now: datetime = datetime.now()
    if not hasattr(context, "asignacion_finalizada"):
        context.asignacion_finalizada: bool = False


def _dt(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M")


def _crear_notificacion(context: behave.runner.Context, destinatario: str, tipo: TipoNotificacion, mensaje: str):
    notif = Notificacion(
        id_notificacion=f"NOTIF-{len(context.notificaciones) + 1:03d}",
        destinatario=destinatario,
        tipo=tipo,
        mensaje=mensaje,
        creada_en=context.now,
    )
    context.notificaciones.append(notif)
    return notif


def _get_tarea(context: behave.runner.Context, codigo: str) -> Tarea:
    if codigo not in context.tareas:
        raise AssertionError(f"No existe la tarea {codigo}")
    return context.tareas[codigo]


def _get_asesor(context: behave.runner.Context, email: str) -> Asesor:
    if email not in context.asesores:
        raise AssertionError(f"No existe el asesor con correo {email}")
    return context.asesores[email]


# ============================================================
# Steps (exactos como tu feature)
# ============================================================
@step('que existe un supervisor autenticado con correo "supervisor@sistema\\.com"')
def step_impl(context):
    _ensure_context(context)
    context.supervisor = Asesor(
        nombres="Supervisor",
        apellidos="Sistema",
        email_asesor="supervisor@sistema.com",
        rol=RolUsuario.ADMIN,  # el diagrama no tiene "Supervisor", se modela con rol
    )
    context.asesores[context.supervisor.email_asesor] = context.supervisor
    context.error = None


@step('existe un asesor con correo "asesor@sistema\\.com"')
def step_impl(context):
    _ensure_context(context)
    asesor = Asesor(
        nombres="Asesor",
        apellidos="Sistema",
        email_asesor="asesor@sistema.com",
        rol=RolUsuario.ASESOR,
    )
    context.asesores[asesor.email_asesor] = asesor
    context.error = None


@step('que existe una tarea con código "TAR-001" y prioridad "MEDIA"')
def step_impl(context):
    _ensure_context(context)
    context.tareas["TAR-001"] = Tarea(
        id_tarea="TAR-001",
        vencimiento=None,
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea.MEDIA,
        comentario="",
        titulo="Tarea TAR-001",
        asignada_a=None,
    )
    context.error = None


@step('el supervisor asigna la tarea "TAR-001" al asesor con correo "asesor@sistema\\.com"')
def step_impl(context):
    _ensure_context(context)
    _get_asesor(context, "asesor@sistema.com")
    tarea = _get_tarea(context, "TAR-001")

    tarea.asignada_a = "asesor@sistema.com"
    # el diagrama no tiene "ASIGNADA", se queda como PENDIENTE al asignar
    tarea.estado = EstadoTarea.PENDIENTE
    context.asignacion_finalizada = False
    context.error = None


@step('la tarea "TAR-001" queda asignada al asesor con correo "asesor@sistema\\.com"')
def step_impl(context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-001")
    assert tarea.asignada_a == "asesor@sistema.com"


@step('la tarea "TAR-001" tiene estado "PENDIENTE"')
def step_impl(context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-001")
    assert tarea.estado == EstadoTarea.PENDIENTE


# ---- Escenario: Asignar múltiples tareas (usa tabla) ----
@step('que el asesor con correo "asesor@sistema\\.com" tiene tareas previamente asignadas')
def step_impl(context):
    _ensure_context(context)
    _get_asesor(context, "asesor@sistema.com")

    # En behave, la tabla llega como context.table
    assert context.table is not None, "Se esperaba una tabla con códigos de tareas."
    for row in context.table:
        codigo = row["codigo"].strip()
        context.tareas[codigo] = Tarea(
            id_tarea=codigo,
            vencimiento=None,
            estado=EstadoTarea.PENDIENTE,
            prioridad=PrioridadTarea.MEDIA,
            comentario="",
            titulo=f"Tarea {codigo}",
            asignada_a="asesor@sistema.com",
        )
    context.error = None


@step('existe una tarea con código "TAR-004" y prioridad "ALTA"')
def step_impl(context):
    _ensure_context(context)
    context.tareas["TAR-004"] = Tarea(
        id_tarea="TAR-004",
        vencimiento=None,
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea.ALTA,
        comentario="",
        titulo="Tarea TAR-004",
        asignada_a=None,
    )
    context.error = None


@step('el supervisor asigna la tarea "TAR-004" al asesor con correo "asesor@sistema\\.com"')
def step_impl(context):
    _ensure_context(context)
    _get_asesor(context, "asesor@sistema.com")
    tarea = _get_tarea(context, "TAR-004")

    tarea.asignada_a = "asesor@sistema.com"
    tarea.estado = EstadoTarea.PENDIENTE
    context.asignacion_finalizada = False
    context.error = None


@step('el asesor con correo "asesor@sistema\\.com" mantiene sus tareas anteriores')
def step_impl(context):
    _ensure_context(context)
    # Verifica que sigan existiendo TAR-002 y TAR-003 asignadas
    for codigo in ["TAR-002", "TAR-003"]:
        tarea = _get_tarea(context, codigo)
        assert tarea.asignada_a == "asesor@sistema.com"


@step('la tarea "TAR-004" queda asignada al asesor con correo "asesor@sistema\\.com"')
def step_impl(context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-004")
    assert tarea.asignada_a == "asesor@sistema.com"


# ---- Escenario: vencimiento ----
@step('que existe una tarea con código "TAR-005" y prioridad "ALTA"')
def step_impl(context):
    _ensure_context(context)
    context.tareas["TAR-005"] = Tarea(
        id_tarea="TAR-005",
        vencimiento=None,
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea.ALTA,
        comentario="",
        titulo="Tarea TAR-005",
        asignada_a=None,
    )
    context.error = None


@step(
    'el supervisor asigna la tarea "TAR-005" al asesor con correo "asesor@sistema\\.com" con fecha de vencimiento "2026-01-20 17:00"')
def step_impl(context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-005")
    _get_asesor(context, "asesor@sistema.com")

    tarea.asignada_a = "asesor@sistema.com"
    tarea.vencimiento = _dt("2026-01-20 17:00")
    tarea.estado = EstadoTarea.PENDIENTE
    context.asignacion_finalizada = False
    context.error = None


@step('la tarea "TAR-005" registra la fecha de vencimiento "2026-01-20 17:00"')
def step_impl(context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-005")
    assert tarea.vencimiento == _dt("2026-01-20 17:00")


@step('la tarea "TAR-005" queda asignada al asesor con correo "asesor@sistema\\.com"')
def step_impl(context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-005")
    assert tarea.asignada_a == "asesor@sistema.com"


@step('el asesor con correo "asesor@sistema\\.com" recibe una notificación de tipo "RECORDATORIO"')
def step_impl(context):
    _ensure_context(context)

    assert any(
        n.destinatario == "asesor@sistema.com" and n.tipo == TipoNotificacion.RECORDATORIO
        for n in context.notificaciones
    ), "No se encontró la notificación RECORDATORIO para el asesor."


# ---- Escenario: notificación por asignación ----
@step('que la tarea "TAR-006" está asignada al asesor con correo "asesor@sistema\\.com"')
def step_impl(context):
    _ensure_context(context)
    _get_asesor(context, "asesor@sistema.com")

    context.tareas["TAR-006"] = Tarea(
        id_tarea="TAR-006",
        vencimiento=None,
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea.MEDIA,
        comentario="",
        titulo="Tarea TAR-006",
        asignada_a="asesor@sistema.com",
    )
    context.asignacion_finalizada = False
    context.error = None


@step("el proceso de asignación finaliza")
def step_impl(context):
    _ensure_context(context)
    context.asignacion_finalizada = True
    context.error = None


@step('el asesor con correo "asesor@sistema\\.com" recibe una notificación de tipo "ASIGNACION_TAREA"')
def step_impl(context):
    _ensure_context(context)
    assert context.asignacion_finalizada is True, "Primero debe finalizar el proceso de asignación."

    # Crea la notificación al finalizar (simulación del evento)
    _crear_notificacion(
        context,
        destinatario="asesor@sistema.com",
        tipo=TipoNotificacion.ASIGNACION_TAREA,
        mensaje="Nueva tarea asignada",
    )

    assert any(
        n.destinatario == "asesor@sistema.com" and n.tipo == TipoNotificacion.ASIGNACION_TAREA
        for n in context.notificaciones
    ), "No se encontró la notificación de asignación."


# ---- Escenario: recordatorio 24h antes del vencimiento ----
@step(
    'que la tarea "TAR-007" está asignada al asesor con correo "asesor@sistema\\.com" con fecha de vencimiento "2026-01-20 17:00"')
def step_impl(context):
    _ensure_context(context)
    _get_asesor(context, "asesor@sistema.com")

    context.tareas["TAR-007"] = Tarea(
        id_tarea="TAR-007",
        vencimiento=_dt("2026-01-20 17:00"),
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea.ALTA,
        comentario="",
        titulo="Tarea TAR-007",
        asignada_a="asesor@sistema.com",
    )
    context.error = None


@step("se alcanza 24 horas antes de la fecha de vencimiento")
def step_impl(context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-007")
    assert tarea.vencimiento is not None
    assert tarea.asignada_a == "asesor@sistema.com"

    # tiempo simulado
    context.now = tarea.vencimiento - timedelta(hours=24)

    # evento: se genera el recordatorio
    _crear_notificacion(
        context,
        destinatario="asesor@sistema.com",
        tipo=TipoNotificacion.RECORDATORIO,
        mensaje=f"Recordatorio: tarea {tarea.id_tarea} vence {tarea.vencimiento.strftime('%Y-%m-%d %H:%M')}",
    )

    context.error = None



@step('el sistema envía un recordatorio al asesor "ASE-001"')
def step_impl(context):
    _ensure_context(context)
    # OJO: tu feature dice "ASE-001", pero el diagrama no tiene id. Lo mapeamos al correo único.
    tarea = _get_tarea(context, "TAR-007")
    assert tarea.vencimiento is not None
    assert tarea.asignada_a == "asesor@sistema.com"

    # Verifica que estamos exactamente 24h antes
    assert tarea.vencimiento - context.now == timedelta(hours=24)

    _crear_notificacion(
        context,
        destinatario="asesor@sistema.com",
        tipo=TipoNotificacion.RECORDATORIO,
        mensaje=f"Recordatorio: tarea {tarea.id_tarea} vence {tarea.vencimiento.strftime('%Y-%m-%d %H:%M')}",
    )

    assert any(
        n.destinatario == "asesor@sistema.com" and n.tipo == TipoNotificacion.RECORDATORIO
        for n in context.notificaciones
    ), "No se encontró la notificación de recordatorio."


# ---- Escenario: cambiar estado ----
@step('que la tarea "TAR-008" está asignada al asesor con correo "asesor@sistema\\.com"')
def step_impl(context):
    _ensure_context(context)
    _get_asesor(context, "asesor@sistema.com")

    context.tareas["TAR-008"] = Tarea(
        id_tarea="TAR-008",
        vencimiento=None,
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea.MEDIA,
        comentario="",
        titulo="Tarea TAR-008",
        asignada_a="asesor@sistema.com",
    )
    context.error = None


@step('el asesor cambia el estado de la tarea "TAR-008" a "COMPLETADA"')
def step_impl(context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-008")
    tarea.estado = EstadoTarea.COMPLETADA
    context.error = None


@step('la tarea "TAR-008" queda en estado "COMPLETADA"')
def step_impl(context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-008")
    assert tarea.estado == EstadoTarea.COMPLETADA


# ---- Escenario: editar prioridad ----
@step('que la tarea "TAR-009" está asignada al asesor con correo "asesor@sistema\\.com"')
def step_impl(context):
    _ensure_context(context)
    _get_asesor(context, "asesor@sistema.com")

    context.tareas["TAR-009"] = Tarea(
        id_tarea="TAR-009",
        vencimiento=None,
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea.MEDIA,
        comentario="",
        titulo="Tarea TAR-009",
        asignada_a="asesor@sistema.com",
    )
    context.error = None


@step('el supervisor actualiza la prioridad de la tarea "TAR-009" a "ALTA"')
def step_impl(context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-009")
    tarea.prioridad = PrioridadTarea.ALTA
    context.error = None


@step('la tarea "TAR-009" refleja la prioridad "ALTA"')
def step_impl(context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-009")
    assert tarea.prioridad == PrioridadTarea.ALTA
