# -*- coding: utf-8 -*-
# features/steps/reporte_estadisticas_tareas_steps.py

import behave.runner
from behave import step, use_step_matcher

from typing import Tuple
from SGPM.domain.entities import *
from SGPM.domain.enums import *
from SGPM.domain.value_objects import *
use_step_matcher("re")


# ============================================================
# Helpers
# ============================================================
def _ensure_context(context: behave.runner.Context):
    # reinicio por escenario (evita arrastre de datos entre escenarios)
    scenario_name = getattr(getattr(context, "scenario", None), "name", None)
    if getattr(context, "_scenario_name", None) != scenario_name:
        context._scenario_name = scenario_name

        context.supervisor: Optional[Asesor] = None
        context.asesores: Dict[str, Asesor] = {}
        context.tareas: List[Tarea] = []
        context.reporte: Optional[ReporteTareas] = None
        context.exportado: Optional[dict] = None
        context.now: datetime = datetime.now()

        # auxiliares para asserts
        context.tarea_vencida_ref: Optional[str] = None
        context.ranking_completadas: List[Tuple[str, int]] = []
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
    if not hasattr(context, "ranking_completadas"):
        context.ranking_completadas = []


def _dt(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M")


def _get_asesor(context: behave.runner.Context, email: str) -> Asesor:
    if email not in context.asesores:
        raise AssertionError(f"No existe el asesor con correo {email}")
    return context.asesores[email]


def _crear_tarea(
    context: behave.runner.Context,
    codigo: str,
    asesor_email: str,
    estado: EstadoTarea,
    prioridad: PrioridadTarea,
    vencimiento: datetime,
    titulo: str = "",
    comentario: str = "",
):
    asesor = _get_asesor(context, asesor_email)
    t = Tarea(
        id_tarea=codigo,
        vencimiento=vencimiento,
        estado=estado,
        prioridad=prioridad,
        comentario=comentario,
        titulo=titulo or f"Tarea {codigo}",
        asignada_a=asesor,  # RELACIÓN (no string)
    )
    context.tareas.append(t)
    return t


def _filtrar_tareas_por_periodo(tareas: List[Tarea], desde: datetime, hasta: datetime) -> List[Tarea]:
    # Para este proyecto usamos vencimiento como referencia temporal del reporte (según tu base)
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
        # vencida si no completada/cancelada y vencimiento < now
        if t.estado in (EstadoTarea.PENDIENTE, EstadoTarea.EN_PROGRESO) and t.vencimiento < now:
            email = t.asignada_a.email_asesor
            res[email] = res.get(email, 0) + 1
    return res


def _completadas_por_asesor(tareas: List[Tarea]) -> Dict[str, int]:
    res: Dict[str, int] = {}
    for t in tareas:
        if t.estado == EstadoTarea.COMPLETADA:
            email = t.asignada_a.email_asesor
            res[email] = res.get(email, 0) + 1
    return res


def _generar_reporte(
    context: behave.runner.Context,
    filtro: FiltroReporteTareas,
    now: Optional[datetime] = None
) -> ReporteTareas:
    now = now or context.now

    tareas = context.tareas

    # filtro por asesor si aplica
    if filtro.asesor_email:
        tareas = [t for t in tareas if t.asignada_a.email_asesor == filtro.asesor_email]

    tareas_periodo = _filtrar_tareas_por_periodo(tareas, filtro.desde, filtro.hasta)

    por_estado = _contar_por_estado(tareas_periodo)
    por_prioridad = _contar_por_prioridad(tareas_periodo)

    vencidas_por = _vencidas_por_asesor(tareas_periodo, now)
    completadas_por = _completadas_por_asesor(tareas_periodo)

    estadisticas = EstadisticasTareas(
        total_tareas=len(tareas_periodo),
        por_estado=por_estado,
        por_prioridad=por_prioridad,
        vencidas_total=sum(vencidas_por.values()),
        vencidas_por_asesor=vencidas_por,
        completadas_por_asesor=completadas_por,
    )

    # ranking auxiliar (no es atributo del diagrama)
    context.ranking_completadas = sorted(
        completadas_por.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return ReporteTareas(
        id_reporte=f"REP-{filtro.desde.strftime('%Y%m%d')}-{filtro.hasta.strftime('%Y%m%d')}",
        creado_en=now,
        filtro=filtro,
        estadisticas=estadisticas,
    )


# ============================================================
# Steps (exactos como tu feature)
# ============================================================

@step(r'que el supervisor con correo "supervisor@sistema\.com" está autenticado')
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


@step(r'existe el asesor con correo "asesor@sistema\.com"')
def step_existe_asesor(context: behave.runner.Context):
    _ensure_context(context)
    asesor = Asesor(
        nombres="Asesor",
        apellidos="Sistema",
        email_asesor="asesor@sistema.com",
        rol=RolUsuario.ASESOR,
    )
    context.asesores[asesor.email_asesor] = asesor


@step(r'existen tareas asignadas al asesor con correo "asesor@sistema\.com" con distintos estados, prioridades y vencimientos')
def step_existen_tareas_base(context: behave.runner.Context):
    _ensure_context(context)
    # Dataset determinístico (enero tiene 4 dentro del periodo; febrero 1 fuera)
    _crear_tarea(context, "TAR-R1", "asesor@sistema.com", EstadoTarea.PENDIENTE, PrioridadTarea.BAJA, _dt("2026-01-05 10:00"))
    _crear_tarea(context, "TAR-R2", "asesor@sistema.com", EstadoTarea.EN_PROGRESO, PrioridadTarea.MEDIA, _dt("2026-01-10 12:00"))
    _crear_tarea(context, "TAR-R3", "asesor@sistema.com", EstadoTarea.COMPLETADA, PrioridadTarea.ALTA, _dt("2026-01-15 09:00"))
    _crear_tarea(context, "TAR-R4", "asesor@sistema.com", EstadoTarea.CANCELADA, PrioridadTarea.CRITICA, _dt("2026-01-25 18:00"))
    _crear_tarea(context, "TAR-R5", "asesor@sistema.com", EstadoTarea.COMPLETADA, PrioridadTarea.MEDIA, _dt("2026-02-02 10:00"))


# ------------------ Reporte por asesor ------------------
@step(r'el supervisor genera un reporte de tareas para el asesor con correo "asesor@sistema\.com" desde "2026-01-01 00:00" hasta "2026-01-31 23:59"')
def step_generar_reporte_por_asesor(context: behave.runner.Context):
    _ensure_context(context)
    filtro = FiltroReporteTareas(
        desde=_dt("2026-01-01 00:00"),
        hasta=_dt("2026-01-31 23:59"),
        asesor_email="asesor@sistema.com",
    )
    context.reporte = _generar_reporte(context, filtro)


@step(r'el reporte muestra el total de tareas del asesor con correo "asesor@sistema\.com" dentro del periodo')
def step_total_por_asesor(context: behave.runner.Context):
    _ensure_context(context)
    assert context.reporte is not None
    assert context.reporte.filtro.asesor_email == "asesor@sistema.com"
    assert context.reporte.estadisticas.total_tareas == 4


@step(r'el reporte desglosa las tareas por estado "PENDIENTE", "EN_PROGRESO", "COMPLETADA" y "CANCELADA"')
def step_desglose_por_estado(context: behave.runner.Context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None

    por_estado = r.estadisticas.por_estado

    # llaves completas
    for e in EstadoTarea:
        assert e in por_estado

    # consistencia
    assert sum(por_estado.values()) == r.estadisticas.total_tareas

    # valores esperados del dataset (por asesor/enero)
    if r.filtro.asesor_email == "asesor@sistema.com" and r.estadisticas.total_tareas == 4:
        assert por_estado[EstadoTarea.PENDIENTE] == 1
        assert por_estado[EstadoTarea.EN_PROGRESO] == 1
        assert por_estado[EstadoTarea.COMPLETADA] == 1
        assert por_estado[EstadoTarea.CANCELADA] == 1


@step(r'el reporte desglosa las tareas por prioridad "BAJA", "MEDIA", "ALTA" y "CRITICA"')
def step_desglose_por_prioridad(context: behave.runner.Context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None

    por_prio = r.estadisticas.por_prioridad

    for p in PrioridadTarea:
        assert p in por_prio

    assert sum(por_prio.values()) == r.estadisticas.total_tareas

    # valores esperados del dataset (por asesor/enero)
    if r.filtro.asesor_email == "asesor@sistema.com" and r.estadisticas.total_tareas == 4:
        assert por_prio[PrioridadTarea.BAJA] == 1
        assert por_prio[PrioridadTarea.MEDIA] == 1
        assert por_prio[PrioridadTarea.ALTA] == 1
        assert por_prio[PrioridadTarea.CRITICA] == 1


# ------------------ Reporte global ------------------
@step(r'el supervisor genera un reporte global de tareas desde "2026-01-01 00:00" hasta "2026-01-31 23:59"')
def step_generar_reporte_global(context: behave.runner.Context):
    _ensure_context(context)

    # agrega otro asesor y 2 tareas completadas dentro del periodo
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


@step(r'el reporte muestra el total de tareas del periodo')
def step_total_global(context: behave.runner.Context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None
    # enero: 4 del asesor1 + 2 del asesor2 = 6
    assert r.estadisticas.total_tareas == 6


# ------------------ Vencidas ------------------
@step(r'que existe una tarea "PENDIENTE" asignada al asesor con correo "asesor@sistema\.com" con vencimiento "2026-01-20 17:00"')
def step_existe_tarea_pendiente_vencimiento(context: behave.runner.Context):
    _ensure_context(context)
    # asegura asesor principal
    if "asesor@sistema.com" not in context.asesores:
        context.asesores["asesor@sistema.com"] = Asesor("Asesor", "Sistema", "asesor@sistema.com", RolUsuario.ASESOR)

    _crear_tarea(context, "TAR-V1", "asesor@sistema.com", EstadoTarea.PENDIENTE, PrioridadTarea.ALTA, _dt("2026-01-20 17:00"))
    context.tarea_vencida_ref = "TAR-V1"


@step(r'el supervisor genera un reporte de tareas vencidas al momento "2026-01-21 10:00"')
def step_generar_reporte_vencidas(context: behave.runner.Context):
    _ensure_context(context)
    now = _dt("2026-01-21 10:00")
    filtro = FiltroReporteTareas(
        desde=_dt("2026-01-01 00:00"),
        hasta=_dt("2026-01-31 23:59"),
        asesor_email=None,
    )
    context.reporte = _generar_reporte(context, filtro, now=now)
    context.now = now


@step(r'el reporte incluye la tarea como "VENCIDA"')
def step_incluye_tarea_vencida(context: behave.runner.Context):
    _ensure_context(context)
    assert context.reporte is not None
    assert context.tarea_vencida_ref is not None

    tarea = next((t for t in context.tareas if t.id_tarea == context.tarea_vencida_ref), None)
    assert tarea is not None

    assert tarea.vencimiento < context.now
    assert tarea.estado in (EstadoTarea.PENDIENTE, EstadoTarea.EN_PROGRESO)

    # coherencia con estadísticas
    vencidas_por = context.reporte.estadisticas.vencidas_por_asesor
    assert vencidas_por.get("asesor@sistema.com", 0) >= 1


@step(r'el reporte muestra la cantidad total de tareas vencidas por asesor')
def step_total_vencidas_por_asesor(context: behave.runner.Context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None
    assert isinstance(r.estadisticas.vencidas_por_asesor, dict)
    # debe existir al menos una entrada si hay vencidas
    assert r.estadisticas.vencidas_total == sum(r.estadisticas.vencidas_por_asesor.values())
    assert r.estadisticas.vencidas_por_asesor.get("asesor@sistema.com", 0) >= 1


# ------------------ Desempeño completadas ------------------
@step(r'que existen tareas en estado "COMPLETADA" registradas para distintos asesores en el periodo desde "2026-01-01 00:00" hasta "2026-01-31 23:59"')
def step_existen_completadas_varios_asesores(context: behave.runner.Context):
    _ensure_context(context)

    if "asesor@sistema.com" not in context.asesores:
        context.asesores["asesor@sistema.com"] = Asesor("Asesor", "Sistema", "asesor@sistema.com", RolUsuario.ASESOR)
    if "asesor2@sistema.com" not in context.asesores:
        context.asesores["asesor2@sistema.com"] = Asesor("Asesor", "Dos", "asesor2@sistema.com", RolUsuario.ASESOR)

    _crear_tarea(context, "TAR-C1", "asesor@sistema.com", EstadoTarea.COMPLETADA, PrioridadTarea.MEDIA, _dt("2026-01-03 09:00"))
    _crear_tarea(context, "TAR-C2", "asesor2@sistema.com", EstadoTarea.COMPLETADA, PrioridadTarea.MEDIA, _dt("2026-01-04 09:00"))
    _crear_tarea(context, "TAR-C3", "asesor2@sistema.com", EstadoTarea.COMPLETADA, PrioridadTarea.ALTA, _dt("2026-01-06 09:00"))


@step(r'el supervisor genera un reporte de desempeño por tareas completadas desde "2026-01-01 00:00" hasta "2026-01-31 23:59"')
def step_generar_reporte_desempeno(context: behave.runner.Context):
    _ensure_context(context)
    filtro = FiltroReporteTareas(
        desde=_dt("2026-01-01 00:00"),
        hasta=_dt("2026-01-31 23:59"),
        asesor_email=None,
    )
    context.reporte = _generar_reporte(context, filtro)


@step(r'el reporte muestra el total de tareas "COMPLETADA" por asesor')
def step_muestra_completadas_por_asesor(context: behave.runner.Context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None
    completadas = r.estadisticas.completadas_por_asesor
    assert isinstance(completadas, dict)
    assert any(v > 0 for v in completadas.values())


@step(r'el reporte presenta a los asesores ordenados de mayor a menor según tareas "COMPLETADA"')
def step_orden_ranking_completadas(context: behave.runner.Context):
    _ensure_context(context)
    r = context.reporte
    assert r is not None

    ranking = context.ranking_completadas
    for i in range(len(ranking) - 1):
        assert ranking[i][1] >= ranking[i + 1][1]


# ------------------ Exportar reporte ------------------
@step(r'que el supervisor tiene un reporte generado para el periodo desde "2026-01-01 00:00" hasta "2026-01-31 23:59"')
def step_supervisor_tiene_reporte_generado(context: behave.runner.Context):
    _ensure_context(context)
    filtro = FiltroReporteTareas(
        desde=_dt("2026-01-01 00:00"),
        hasta=_dt("2026-01-31 23:59"),
        asesor_email=None,
    )
    context.reporte = _generar_reporte(context, filtro)


@step(r'el supervisor solicita exportar el reporte en formato "PDF"')
def step_exportar_pdf(context: behave.runner.Context):
    _ensure_context(context)
    assert context.reporte is not None

    r = context.reporte
    est = r.estadisticas

    context.exportado = {
        "formato": "PDF",
        "reporte_id": r.id_reporte,
        "creado_en": r.creado_en,
        "contenido": {
            "total_tareas": est.total_tareas,
            "por_estado": {k.value: v for k, v in est.por_estado.items()},
            "por_prioridad": {k.value: v for k, v in est.por_prioridad.items()},
            "vencidas_total": est.vencidas_total,
            "vencidas_por_asesor": dict(est.vencidas_por_asesor),
            "completadas_por_asesor": dict(est.completadas_por_asesor),
        },
    }


@step(r'se obtiene el reporte exportado en formato "PDF"')
def step_obtiene_exportado_pdf(context: behave.runner.Context):
    _ensure_context(context)
    assert context.exportado is not None
    assert context.exportado.get("formato") == "PDF"


@step(r'el reporte exportado conserva los totales y desgloses del reporte generado')
def step_conserva_totales_desgloses(context: behave.runner.Context):
    _ensure_context(context)
    assert context.reporte is not None
    assert context.exportado is not None

    est = context.reporte.estadisticas
    contenido = context.exportado["contenido"]

    assert contenido["total_tareas"] == est.total_tareas
    assert contenido["por_estado"] == {k.value: v for k, v in est.por_estado.items()}
    assert contenido["por_prioridad"] == {k.value: v for k, v in est.por_prioridad.items()}
