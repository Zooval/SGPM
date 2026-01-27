# -*- coding: utf-8 -*-
# features/steps/tareas_steps.py

import behave.runner
from behave import step, use_step_matcher
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

use_step_matcher("re")


# ============================================================
# Enums (según UML)
# ============================================================
class RolUsuario(Enum):
    ASESOR = "ASESOR"
    SUPERVISOR = "SUPERVISOR"


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
# Entidades (según UML)
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
    asignada_a: Optional[Asesor]  # UML: Tarea "*" --> "1" Asesor : asignada_a


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


def _crear_tarea(context: behave.runner.Context, codigo: str, prioridad: str):
    context.tareas[codigo] = Tarea(
        id_tarea=codigo,
        vencimiento=None,
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea[prioridad],
        comentario="",
        titulo=f"Tarea {codigo}",
        asignada_a=None,
    )


def _asignar_tarea_a_asesor(context: behave.runner.Context, codigo_tarea: str, email_asesor: str):
    tarea = _get_tarea(context, codigo_tarea)
    asesor = _get_asesor(context, email_asesor)
    tarea.asignada_a = asesor
    # UML no define estado "ASIGNADA": al asignar se mantiene PENDIENTE
    if tarea.estado is None:
        tarea.estado = EstadoTarea.PENDIENTE
    context.asignacion_finalizada = False


# ============================================================
# Steps (exactos como el .feature)
# ============================================================

# ---------- Antecedentes ----------
@step(r'que existe un supervisor autenticado con correo "supervisor@sistema\.com"')
def step_supervisor_autenticado(context: behave.runner.Context):
    _ensure_context(context)
    supervisor = Asesor(
        nombres="Supervisor",
        apellidos="Sistema",
        email_asesor="supervisor@sistema.com",
        rol=RolUsuario.SUPERVISOR,
    )
    context.supervisor = supervisor
    context.asesores[supervisor.email_asesor] = supervisor
    context.error = None


@step(r'existe un asesor con correo "asesor@sistema\.com"')
def step_existe_asesor(context: behave.runner.Context):
    _ensure_context(context)
    asesor = Asesor(
        nombres="Asesor",
        apellidos="Sistema",
        email_asesor="asesor@sistema.com",
        rol=RolUsuario.ASESOR,
    )
    context.asesores[asesor.email_asesor] = asesor
    context.error = None


# ---------- Escenario: Asignar una tarea a un asesor ----------
@step(r'que existe una tarea con código "TAR-001" y prioridad "MEDIA"')
def step_existe_tarea_tar001_media(context: behave.runner.Context):
    _ensure_context(context)
    _crear_tarea(context, "TAR-001", "MEDIA")
    context.error = None


@step(r'el supervisor asigna la tarea "TAR-001" al asesor con correo "asesor@sistema\.com"')
def step_supervisor_asigna_tar001(context: behave.runner.Context):
    _ensure_context(context)
    _asignar_tarea_a_asesor(context, "TAR-001", "asesor@sistema.com")
    context.error = None


@step(r'la tarea "TAR-001" queda asignada al asesor con correo "asesor@sistema\.com"')
def step_validar_asignacion_tar001(context: behave.runner.Context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-001")
    assert tarea.asignada_a is not None
    assert tarea.asignada_a.email_asesor == "asesor@sistema.com"


@step(r'la tarea "TAR-001" tiene estado "PENDIENTE"')
def step_validar_estado_tar001(context: behave.runner.Context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-001")
    assert tarea.estado == EstadoTarea.PENDIENTE


# ---------- Escenario: Asignar múltiples tareas ----------
@step(r'que el asesor con correo "asesor@sistema\.com" tiene tareas previamente asignadas')
def step_asesor_tiene_tareas_previas(context: behave.runner.Context):
    _ensure_context(context)
    asesor = _get_asesor(context, "asesor@sistema.com")

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
            asignada_a=asesor,
        )
    context.error = None


@step(r'existe una tarea con código "TAR-004" y prioridad "ALTA"')
def step_existe_tarea_tar004_alta(context: behave.runner.Context):
    _ensure_context(context)
    _crear_tarea(context, "TAR-004", "ALTA")
    context.error = None


@step(r'el supervisor asigna la tarea "TAR-004" al asesor con correo "asesor@sistema\.com"')
def step_supervisor_asigna_tar004(context: behave.runner.Context):
    _ensure_context(context)
    _asignar_tarea_a_asesor(context, "TAR-004", "asesor@sistema.com")
    context.error = None


@step(r'el asesor con correo "asesor@sistema\.com" mantiene sus tareas anteriores')
def step_asesor_mantiene_tareas(context: behave.runner.Context):
    _ensure_context(context)
    for codigo in ["TAR-002", "TAR-003"]:
        tarea = _get_tarea(context, codigo)
        assert tarea.asignada_a is not None
        assert tarea.asignada_a.email_asesor == "asesor@sistema.com"


@step(r'la tarea "TAR-004" queda asignada al asesor con correo "asesor@sistema\.com"')
def step_validar_asignacion_tar004(context: behave.runner.Context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-004")
    assert tarea.asignada_a is not None
    assert tarea.asignada_a.email_asesor == "asesor@sistema.com"


# ---------- Escenario: Asignar una tarea con fecha de vencimiento ----------
@step(r'que existe una tarea con código "TAR-005" y prioridad "ALTA"')
def step_existe_tarea_tar005_alta(context: behave.runner.Context):
    _ensure_context(context)
    _crear_tarea(context, "TAR-005", "ALTA")
    context.error = None


@step(r'el supervisor asigna la tarea "TAR-005" al asesor con correo "asesor@sistema\.com" con fecha de vencimiento "2026-01-20 17:00"')
def step_asignar_tar005_con_vencimiento(context: behave.runner.Context):
    _ensure_context(context)
    _asignar_tarea_a_asesor(context, "TAR-005", "asesor@sistema.com")
    tarea = _get_tarea(context, "TAR-005")
    tarea.vencimiento = _dt("2026-01-20 17:00")
    tarea.estado = EstadoTarea.PENDIENTE
    context.error = None


@step(r'la tarea "TAR-005" registra la fecha de vencimiento "2026-01-20 17:00"')
def step_validar_vencimiento_tar005(context: behave.runner.Context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-005")
    assert tarea.vencimiento == _dt("2026-01-20 17:00")


@step(r'la tarea "TAR-005" queda asignada al asesor con correo "asesor@sistema\.com"')
def step_validar_asignacion_tar005(context: behave.runner.Context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-005")
    assert tarea.asignada_a is not None
    assert tarea.asignada_a.email_asesor == "asesor@sistema.com"


# ---------- Escenario: Enviar notificación al asesor por tarea asignada ----------
@step(r'que la tarea "TAR-006" está asignada al asesor con correo "asesor@sistema\.com"')
def step_tarea_tar006_asignada(context: behave.runner.Context):
    _ensure_context(context)
    asesor = _get_asesor(context, "asesor@sistema.com")

    context.tareas["TAR-006"] = Tarea(
        id_tarea="TAR-006",
        vencimiento=None,
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea.MEDIA,
        comentario="",
        titulo="Tarea TAR-006",
        asignada_a=asesor,
    )
    context.asignacion_finalizada = False
    context.error = None


@step(r'el proceso de asignación finaliza')
def step_proceso_asignacion_finaliza(context: behave.runner.Context):
    _ensure_context(context)
    context.asignacion_finalizada = True

    # Evento: al finalizar, se notifica al asesor por asignación
    _crear_notificacion(
        context,
        destinatario="asesor@sistema.com",
        tipo=TipoNotificacion.ASIGNACION_TAREA,
        mensaje="Nueva tarea asignada",
    )
    context.error = None


@step(r'el asesor con correo "asesor@sistema\.com" recibe una notificación de tipo "ASIGNACION_TAREA"')
def step_validar_notificacion_asignacion(context: behave.runner.Context):
    _ensure_context(context)
    assert context.asignacion_finalizada is True, "Primero debe finalizar el proceso de asignación."

    assert any(
        n.destinatario == "asesor@sistema.com" and n.tipo == TipoNotificacion.ASIGNACION_TAREA
        for n in context.notificaciones
    ), "No se encontró la notificación ASIGNACION_TAREA para el asesor."


# ---------- Escenario: Enviar recordatorio antes del vencimiento ----------
@step(r'que la tarea "TAR-007" está asignada al asesor con correo "asesor@sistema\.com" con fecha de vencimiento "2026-01-20 17:00"')
def step_tarea_tar007_asignada_con_vencimiento(context: behave.runner.Context):
    _ensure_context(context)
    asesor = _get_asesor(context, "asesor@sistema.com")

    context.tareas["TAR-007"] = Tarea(
        id_tarea="TAR-007",
        vencimiento=_dt("2026-01-20 17:00"),
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea.ALTA,
        comentario="",
        titulo="Tarea TAR-007",
        asignada_a=asesor,
    )
    context.error = None


@step(r'se alcanza 24 horas antes de la fecha de vencimiento')
def step_24_horas_antes_vencimiento(context: behave.runner.Context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-007")
    assert tarea.vencimiento is not None
    assert tarea.asignada_a is not None
    assert tarea.asignada_a.email_asesor == "asesor@sistema.com"

    context.now = tarea.vencimiento - timedelta(hours=24)

    # Evento: al llegar a 24h antes, se envía RECORDATORIO
    _crear_notificacion(
        context,
        destinatario="asesor@sistema.com",
        tipo=TipoNotificacion.RECORDATORIO,
        mensaje=f"Recordatorio: tarea {tarea.id_tarea} vence {tarea.vencimiento.strftime('%Y-%m-%d %H:%M')}",
    )
    context.error = None


@step(r'el asesor con correo "asesor@sistema\.com" recibe una notificación de tipo "RECORDATORIO"')
def step_validar_notificacion_recordatorio(context: behave.runner.Context):
    _ensure_context(context)
    assert any(
        n.destinatario == "asesor@sistema.com" and n.tipo == TipoNotificacion.RECORDATORIO
        for n in context.notificaciones
    ), "No se encontró la notificación RECORDATORIO para el asesor."


# ---------- Escenario: Cambiar estado de una tarea ----------
@step(r'que la tarea "TAR-008" está asignada al asesor con correo "asesor@sistema\.com"')
def step_tarea_tar008_asignada(context: behave.runner.Context):
    _ensure_context(context)
    asesor = _get_asesor(context, "asesor@sistema.com")

    context.tareas["TAR-008"] = Tarea(
        id_tarea="TAR-008",
        vencimiento=None,
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea.MEDIA,
        comentario="",
        titulo="Tarea TAR-008",
        asignada_a=asesor,
    )
    context.error = None


@step(r'el asesor cambia el estado de la tarea "TAR-008" a "COMPLETADA"')
def step_cambiar_estado_tar008(context: behave.runner.Context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-008")
    tarea.estado = EstadoTarea.COMPLETADA
    context.error = None


@step(r'la tarea "TAR-008" queda en estado "COMPLETADA"')
def step_validar_estado_tar008(context: behave.runner.Context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-008")
    assert tarea.estado == EstadoTarea.COMPLETADA


# ---------- Escenario: Editar una tarea asignada ----------
@step(r'que la tarea "TAR-009" está asignada al asesor con correo "asesor@sistema\.com"')
def step_tarea_tar009_asignada(context: behave.runner.Context):
    _ensure_context(context)
    asesor = _get_asesor(context, "asesor@sistema.com")

    context.tareas["TAR-009"] = Tarea(
        id_tarea="TAR-009",
        vencimiento=None,
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea.MEDIA,
        comentario="",
        titulo="Tarea TAR-009",
        asignada_a=asesor,
    )
    context.error = None


@step(r'el supervisor actualiza la prioridad de la tarea "TAR-009" a "ALTA"')
def step_actualizar_prioridad_tar009(context: behave.runner.Context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-009")
    tarea.prioridad = PrioridadTarea.ALTA
    context.error = None


@step(r'la tarea "TAR-009" refleja la prioridad "ALTA"')
def step_validar_prioridad_tar009(context: behave.runner.Context):
    _ensure_context(context)
    tarea = _get_tarea(context, "TAR-009")
    assert tarea.prioridad == PrioridadTarea.ALTA
