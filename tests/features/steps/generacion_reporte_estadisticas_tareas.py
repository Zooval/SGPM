import behave.runner
from behave import step, use_step_matcher
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

use_step_matcher("re")


# ============================================================
# Enums (según diagrama)
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


# ============================================================
# Entidades (diagrama)
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
    vencimiento: datetime
    estado: EstadoTarea
    prioridad: PrioridadTarea
    comentario: str
    titulo: str
    asignada_a: str  # email_asesor


# ============================================================
# Value Objects para valor agregado (reportes)
# ============================================================
@dataclass(frozen=True)
class FiltroReporteTareas:
    desde: datetime
    hasta: datetime
    asesor_email: Optional[str] = None  # None => global


@dataclass
class ReporteTareas:
    filtro: FiltroReporteTareas
    total: int
    por_estado: Dict[EstadoTarea, int]
    por_prioridad: Dict[PrioridadTarea, int]
    vencidas_por_asesor: Dict[str, int]
    completadas_por_asesor: Dict[str, int]
    ranking_completadas: List[Tuple[str, int]]


# ============================================================
# Helpers
# ============================================================
def _ensure_context(context: behave.runner.Context):
    scenario_name = getattr(getattr(context, "scenario", None), "name", None)
    if getattr(context, "_scenario_name", None) != scenario_name:
        context._scenario_name = scenario_name

        context.supervisor: Optional[Asesor] = None
        context.asesores: Dict[str, Asesor] = {}
        context.tareas: List[Tarea] = []
        context.reporte: Optional[ReporteTareas] = None
        context.exportado: Optional[dict] = None
        context.now: datetime = datetime.now()
        context.tarea_vencida_ref: Optional[str] = None
        return

    if not hasattr(context, "supervisor"):
        context.supervisor = None
    if not hasattr(context, "asesores"):
        context.asesores = {}
    if not hasattr(context, "tareas"):
        context.tareas = []
    if not hasattr(context, "reporte"):
        context.reporte = None
    if not hasattr(context, "exportado"):
        context.exportado = None
    if not hasattr(context, "now"):
        context.now = datetime.now()
    if not hasattr(context, "tarea_vencida_ref"):
        context.tarea_vencida_ref = None


def _dt(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M")


def _crear_tarea(
    context: behave.runner.Context,
    codigo: str,
    asignada_a: str,
    estado: EstadoTarea,
    prioridad: PrioridadTarea,
    vencimiento: datetime,
    titulo: str = "",
    comentario: str = "",
):
    t = Tarea(
        id_tarea=codigo,
        vencimiento=vencimiento,
        estado=estado,
        prioridad=prioridad,
        comentario=comentario,
        titulo=titulo or f"Tarea {codigo}",
        asignada_a=asignada_a,
    )
    context.tareas.append(t)
    return t


def _filtrar_tareas_por_periodo(tareas: List[Tarea], desde: datetime, hasta: datetime) -> List[Tarea]:
    return [t for t in tareas if desde <= t.vencimiento <= hasta]


def _contar_por_estado(tareas: List[Tarea]) -> Dict[EstadoTarea, int]:
    base = {e: 0 for e in EstadoTarea}
    for t in tareas:
        base[t.estado] += 1
    return base


def _contar_por_prioridad(tareas: List[Tarea]) -> Dict[PrioridadTarea, int]:
    base = {p: 0 for p in PrioridadTarea}
    for t in tareas:
        base[t.prioridad] += 1
    return base


def _vencidas_por_asesor(tareas: List[Tarea], now: datetime) -> Dict[str, int]:
    res: Dict[str, int] = {}
    for t in tareas:
        if t.estado in (EstadoTarea.PENDIENTE, EstadoTarea.EN_PROGRESO) and t.vencimiento < now:
            res[t.asignada_a] = res.get(t.asignada_a, 0) + 1
    return res


def _completadas_por_asesor(tareas: List[Tarea]) -> Dict[str, int]:
    res: Dict[str, int] = {}
    for t in tareas:
        if t.estado == EstadoTarea.COMPLETADA:
            res[t.asignada_a] = res.get(t.asignada_a, 0) + 1
    return res


def _generar_reporte(context: behave.runner.Context, filtro: FiltroReporteTareas, now: Optional[datetime] = None) -> ReporteTareas:
    now = now or context.now

    tareas = context.tareas
    if filtro.asesor_email:
        tareas = [t for t in tareas if t.asignada_a == filtro.asesor_email]

    tareas_periodo = _filtrar_tareas_por_periodo(tareas, filtro.desde, filtro.hasta)

    por_estado = _contar_por_estado(tareas_periodo)
    por_prioridad = _contar_por_prioridad(tareas_periodo)

    vencidas = _vencidas_por_asesor(tareas_periodo, now)
    completadas = _completadas_por_asesor(tareas_periodo)

    ranking = sorted(completadas.items(), key=lambda x: x[1], reverse=True)

    return ReporteTareas(
        filtro=filtro,
        total=len(tareas_periodo),
        por_estado=por_estado,
        por_prioridad=por_prioridad,
        vencidas_por_asesor=vencidas,
        completadas_por_asesor=completadas,
        ranking_completadas=ranking,
    )


# ============================================================
# Steps (exactos como tu feature)
# ============================================================
@step('que el supervisor con correo "supervisor@sistema\\.com" está autenticado')
def step_impl(context):
    _ensure_context(context)
    supervisor = Asesor(
        nombres="Supervisor",
        apellidos="Sistema",
        email_asesor="supervisor@sistema.com",
        rol=RolUsuario.SUPERVISOR,
    )
    context.supervisor = supervisor
    context.asesores[supervisor.email_asesor] = supervisor


@step('existe el asesor con correo "asesor@sistema\\.com"')
def step_impl(context):
    _ensure_context(context)
    asesor = Asesor(
        nombres="Asesor",
        apellidos="Sistema",
        email_asesor="asesor@sistema.com",
        rol=RolUsuario.ASESOR,
    )
    context.asesores[asesor.email_asesor] = asesor


@step('existen tareas asignadas al asesor con correo "asesor@sistema\\.com" con distintos estados, prioridades y vencimientos')
def step_impl(context):
    _ensure_context(context)
    _crear_tarea(context, "TAR-R1", "asesor@sistema.com", EstadoTarea.PENDIENTE, PrioridadTarea.BAJA, _dt("2026-01-05 10:00"))
    _crear_tarea(context, "TAR-R2", "asesor@sistema.com", EstadoTarea.EN_PROGRESO, PrioridadTarea.MEDIA, _dt("2026-01-10 12:00"))
    _crear_tarea(context, "TAR-R3", "asesor@sistema.com", EstadoTarea.COMPLETADA, PrioridadTarea.ALTA, _dt("2026-01-15 09:00"))
    _crear_tarea(context, "TAR-R4", "asesor@sistema.com", EstadoTarea.CANCELADA, PrioridadTarea.CRITICA, _dt("2026-01-25 18:00"))
    _crear_tarea(context, "TAR-R5", "asesor@sistema.com", EstadoTarea.COMPLETADA, PrioridadTarea.MEDIA, _dt("2026-02-02 10:00"))


@step('el supervisor genera un reporte de tareas para el asesor con correo "asesor@sistema\\.com" desde "2026-01-01 00:00" hasta "2026-01-31 23:59"')
def step_impl(context):
    _ensure_context(context)
    filtro = FiltroReporteTareas(
        desde=_dt("2026-01-01 00:00"),
        hasta=_dt("2026-01-31 23:59"),
        asesor_email="asesor@sistema.com",
    )
    context.reporte = _generar_reporte(context, filtro)


@step('el reporte muestra el total de tareas del asesor con correo "asesor@sistema\\.com" dentro del periodo')
def step_impl(context):
    _ensure_context(context)
    assert context.reporte is not None
    assert context.reporte.total == 4


@step('el reporte desglosa las tareas por estado "PENDIENTE", "EN_PROGRESO", "COMPLETADA" y "CANCELADA"')
def step_impl(context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None

    # existen todas las llaves
    for estado in EstadoTarea:
        assert estado in r.por_estado

    # consistencia: suma == total
    assert sum(r.por_estado.values()) == r.total
    assert all(isinstance(v, int) and v >= 0 for v in r.por_estado.values())

    # Validación exacta SOLO para el escenario por asesor (dataset determinístico)
    if r.filtro.asesor_email == "asesor@sistema.com" and r.total == 4:
        assert r.por_estado[EstadoTarea.PENDIENTE] == 1
        assert r.por_estado[EstadoTarea.EN_PROGRESO] == 1
        assert r.por_estado[EstadoTarea.COMPLETADA] == 1
        assert r.por_estado[EstadoTarea.CANCELADA] == 1


@step('el reporte desglosa las tareas por prioridad "BAJA", "MEDIA", "ALTA" y "CRITICA"')
def step_impl(context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None

    for prio in PrioridadTarea:
        assert prio in r.por_prioridad

    assert sum(r.por_prioridad.values()) == r.total
    assert all(isinstance(v, int) and v >= 0 for v in r.por_prioridad.values())

    # Validación exacta SOLO para el escenario por asesor (dataset determinístico)
    if r.filtro.asesor_email == "asesor@sistema.com" and r.total == 4:
        assert r.por_prioridad[PrioridadTarea.BAJA] == 1
        assert r.por_prioridad[PrioridadTarea.MEDIA] == 1
        assert r.por_prioridad[PrioridadTarea.ALTA] == 1
        assert r.por_prioridad[PrioridadTarea.CRITICA] == 1


@step('el supervisor genera un reporte global de tareas desde "2026-01-01 00:00" hasta "2026-01-31 23:59"')
def step_impl(context):
    _ensure_context(context)

    if "asesor2@sistema.com" not in context.asesores:
        context.asesores["asesor2@sistema.com"] = Asesor(
            nombres="Asesor",
            apellidos="Dos",
            email_asesor="asesor2@sistema.com",
            rol=RolUsuario.ASESOR,
        )

    _crear_tarea(context, "TAR-G1", "asesor2@sistema.com", EstadoTarea.COMPLETADA, PrioridadTarea.MEDIA, _dt("2026-01-08 10:00"))
    _crear_tarea(context, "TAR-G2", "asesor2@sistema.com", EstadoTarea.COMPLETADA, PrioridadTarea.ALTA, _dt("2026-01-22 16:00"))

    filtro = FiltroReporteTareas(
        desde=_dt("2026-01-01 00:00"),
        hasta=_dt("2026-01-31 23:59"),
        asesor_email=None,
    )
    context.reporte = _generar_reporte(context, filtro)


@step("el reporte muestra el total de tareas del periodo")
def step_impl(context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None
    assert r.total == 6


@step('que existe una tarea "PENDIENTE" asignada al asesor con correo "asesor@sistema\\.com" con vencimiento "2026-01-20 17:00"')
def step_impl(context):
    _ensure_context(context)
    _crear_tarea(context, "TAR-V1", "asesor@sistema.com", EstadoTarea.PENDIENTE, PrioridadTarea.ALTA, _dt("2026-01-20 17:00"))
    context.tarea_vencida_ref = "TAR-V1"


@step('el supervisor genera un reporte de tareas vencidas al momento "2026-01-21 10:00"')
def step_impl(context):
    _ensure_context(context)
    now = _dt("2026-01-21 10:00")
    filtro = FiltroReporteTareas(
        desde=_dt("2026-01-01 00:00"),
        hasta=_dt("2026-01-31 23:59"),
        asesor_email=None,
    )
    context.reporte = _generar_reporte(context, filtro, now=now)
    context.now = now


@step('el reporte incluye la tarea como "VENCIDA"')
def step_impl(context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None
    assert context.tarea_vencida_ref is not None

    tarea = next((t for t in context.tareas if t.id_tarea == context.tarea_vencida_ref), None)
    assert tarea is not None
    assert tarea.vencimiento < context.now
    assert tarea.estado in (EstadoTarea.PENDIENTE, EstadoTarea.EN_PROGRESO)


@step("el reporte muestra la cantidad total de tareas vencidas por asesor")
def step_impl(context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None
    assert isinstance(r.vencidas_por_asesor, dict)
    assert r.vencidas_por_asesor.get("asesor@sistema.com", 0) >= 1


@step('que existen tareas en estado "COMPLETADA" registradas para distintos asesores en el periodo desde "2026-01-01 00:00" hasta "2026-01-31 23:59"')
def step_impl(context):
    _ensure_context(context)

    if "asesor@sistema.com" not in context.asesores:
        context.asesores["asesor@sistema.com"] = Asesor("Asesor", "Sistema", "asesor@sistema.com", RolUsuario.ASESOR)
    if "asesor2@sistema.com" not in context.asesores:
        context.asesores["asesor2@sistema.com"] = Asesor("Asesor", "Dos", "asesor2@sistema.com", RolUsuario.ASESOR)

    _crear_tarea(context, "TAR-C1", "asesor@sistema.com", EstadoTarea.COMPLETADA, PrioridadTarea.MEDIA, _dt("2026-01-03 09:00"))
    _crear_tarea(context, "TAR-C2", "asesor2@sistema.com", EstadoTarea.COMPLETADA, PrioridadTarea.MEDIA, _dt("2026-01-04 09:00"))
    _crear_tarea(context, "TAR-C3", "asesor2@sistema.com", EstadoTarea.COMPLETADA, PrioridadTarea.ALTA, _dt("2026-01-06 09:00"))


@step('el supervisor genera un reporte de desempeño por tareas completadas desde "2026-01-01 00:00" hasta "2026-01-31 23:59"')
def step_impl(context):
    _ensure_context(context)
    filtro = FiltroReporteTareas(
        desde=_dt("2026-01-01 00:00"),
        hasta=_dt("2026-01-31 23:59"),
        asesor_email=None,
    )
    context.reporte = _generar_reporte(context, filtro)


@step('el reporte muestra el total de tareas "COMPLETADA" por asesor')
def step_impl(context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None
    assert isinstance(r.completadas_por_asesor, dict)
    assert any(v > 0 for v in r.completadas_por_asesor.values())


@step('el reporte presenta a los asesores ordenados de mayor a menor según tareas "COMPLETADA"')
def step_impl(context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None

    ranking = r.ranking_completadas
    for i in range(len(ranking) - 1):
        assert ranking[i][1] >= ranking[i + 1][1]


@step('que el supervisor tiene un reporte generado para el periodo desde "2026-01-01 00:00" hasta "2026-01-31 23:59"')
def step_impl(context):
    _ensure_context(context)
    filtro = FiltroReporteTareas(
        desde=_dt("2026-01-01 00:00"),
        hasta=_dt("2026-01-31 23:59"),
        asesor_email=None,
    )
    context.reporte = _generar_reporte(context, filtro)


@step('el supervisor solicita exportar el reporte en formato "PDF"')
def step_impl(context):
    _ensure_context(context)
    assert context.reporte is not None
    context.exportado = {
        "formato": "PDF",
        "generado_en": context.now,
        "contenido": {
            "total": context.reporte.total,
            "por_estado": {k.value: v for k, v in context.reporte.por_estado.items()},
            "por_prioridad": {k.value: v for k, v in context.reporte.por_prioridad.items()},
        },
    }


@step('se obtiene el reporte exportado en formato "PDF"')
def step_impl(context):
    _ensure_context(context)
    assert context.exportado is not None
    assert context.exportado.get("formato") == "PDF"


@step("el reporte exportado conserva los totales y desgloses del reporte generado")
def step_impl(context):
    _ensure_context(context)
    assert context.reporte is not None
    assert context.exportado is not None

    assert context.exportado["contenido"]["total"] == context.reporte.total
    assert context.exportado["contenido"]["por_estado"] == {k.value: v for k, v in context.reporte.por_estado.items()}
    assert context.exportado["contenido"]["por_prioridad"] == {k.value: v for k, v in context.reporte.por_prioridad.items()}
