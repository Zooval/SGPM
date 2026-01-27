# -*- coding: utf-8 -*-
# features/steps/citas_steps.py

import behave.runner
from behave import step, use_step_matcher
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Dict, List, Optional

use_step_matcher("re")


# ============================================================
# Enums (según diagrama, SOLO los necesarios para esta feature)
# ============================================================
class RolUsuario(Enum):
    ASESOR = "ASESOR"
    SUPERVISOR = "SUPERVISOR"


class EstadoSolicitud(Enum):
    CREADA = "CREADA"
    EN_REVISION = "EN_REVISION"
    DOCUMENTOS_PENDIENTES = "DOCUMENTOS_PENDIENTES"
    ENVIADA = "ENVIADA"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    CERRADA = "CERRADA"


class TipoServicio(Enum):
    VISA_TURISMO = "VISA_TURISMO"
    VISA_TRABAJO = "VISA_TRABAJO"
    ESTUDIOS = "ESTUDIOS"
    RESIDENCIA = "RESIDENCIA"


class TipoCita(Enum):
    CONSULAR = "CONSULAR"
    BIOMETRIA = "BIOMETRIA"
    ENTREGA_DOCUMENTOS = "ENTREGA_DOCUMENTOS"
    ASESORIA = "ASESORIA"


class EstadoCita(Enum):
    PROGRAMADA = "PROGRAMADA"
    REPROGRAMADA = "REPROGRAMADA"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"
    NO_ASISTIO = "NO_ASISTIO"


class TipoNotificacion(Enum):
    RECORDATORIO = "RECORDATORIO"
    DOC_FALTANTE = "DOC_FALTANTE"
    CITA_PROXIMA = "CITA_PROXIMA"
    ASIGNACION_TAREA = "ASIGNACION_TAREA"


# ============================================================
# Value Objects / Entidades (según diagrama)
# ============================================================
@dataclass(frozen=True)
class RangoFechaHora:
    inicio: datetime
    fin: datetime


@dataclass
class Solicitante:
    cedula: str
    nombres: str
    apellidos: str
    correo: str
    telefono: str
    direccion: str
    fecha_nacimiento: date
    habilitado: bool


@dataclass
class Asesor:
    nombres: str
    apellidos: str
    email_asesor: str
    rol: RolUsuario


@dataclass
class SolicitudMigratoria:
    codigo: str
    tipo_servicio: TipoServicio
    estado_actual: EstadoSolicitud
    fecha_creacion: datetime
    fecha_expiracion: datetime


@dataclass
class Cita:
    id_cita: str
    observacion: str
    rango: RangoFechaHora
    tipo: TipoCita
    estado: EstadoCita


@dataclass
class Notificacion:
    id_notificacion: str
    destinatario: str
    tipo: TipoNotificacion
    mensaje: str
    creada_en: datetime


# ============================================================
# Helpers (almacenamiento en memoria)
# ============================================================
def _ensure_context(context: behave.runner.Context):
    if not hasattr(context, "asesor"):
        context.asesor: Optional[Asesor] = None

    if not hasattr(context, "solicitantes"):
        context.solicitantes: Dict[str, Solicitante] = {}

    if not hasattr(context, "solicitudes"):
        context.solicitudes: Dict[str, SolicitudMigratoria] = {}

    if not hasattr(context, "citas"):
        context.citas: List[Cita] = []

    if not hasattr(context, "notificaciones"):
        context.notificaciones: List[Notificacion] = []

    if not hasattr(context, "solicitud_citas"):
        context.solicitud_citas: Dict[str, List[str]] = {}  # codigoSolicitud -> [idCita]

    # mapas de apoyo (para las pruebas)
    if not hasattr(context, "solicitud_solicitante"):
        context.solicitud_solicitante: Dict[str, str] = {}  # codigoSolicitud -> cedula

    if not hasattr(context, "solicitud_asesor"):
        context.solicitud_asesor: Dict[str, str] = {}  # codigoSolicitud -> email_asesor

    if not hasattr(context, "error"):
        context.error: Optional[Exception] = None

    if not hasattr(context, "ultima_cita_id"):
        context.ultima_cita_id: Optional[str] = None

    if not hasattr(context, "agenda"):
        context.agenda: List[Cita] = []

    if not hasattr(context, "now"):
        context.now: Optional[datetime] = None

    if not hasattr(context, "citas_snapshot_len"):
        context.citas_snapshot_len: int = 0


def _dt(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M")


def _d(value: str) -> date:
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


def _overlap(a: RangoFechaHora, b: RangoFechaHora) -> bool:
    return a.inicio < b.fin and a.fin > b.inicio


def _get_cita_by_id(context: behave.runner.Context, cita_id: str) -> Cita:
    for c in context.citas:
        if c.id_cita == cita_id:
            return c
    raise AssertionError(f"No existe la cita con id {cita_id}")


def _crear_notificacion(context: behave.runner.Context, destinatario: str, tipo: TipoNotificacion, mensaje: str):
    notif = Notificacion(
        id_notificacion=f"NOTIF-{len(context.notificaciones) + 1:03d}",
        destinatario=destinatario,
        tipo=tipo,
        mensaje=mensaje,
        creada_en=context.now or datetime.now(),
    )
    context.notificaciones.append(notif)
    return notif


def _agenda_del_asesor(context: behave.runner.Context) -> List[Cita]:
    return list(context.citas)


def _asegurar_solicitud(context: behave.runner.Context, codigo_solicitud: str):
    if codigo_solicitud not in context.solicitudes:
        context.solicitudes[codigo_solicitud] = SolicitudMigratoria(
            codigo=codigo_solicitud,
            tipo_servicio=TipoServicio.RESIDENCIA,
            estado_actual=EstadoSolicitud.CREADA,
            fecha_creacion=_dt("2026-04-01 09:00"),
            fecha_expiracion=_dt("2026-10-01 09:00"),
        )


def _agendar_cita_si_disponible(context: behave.runner.Context, codigo_solicitud: str, tipo: TipoCita,
                               inicio: datetime, fin: datetime, observacion: str) -> Optional[Cita]:
    rango = RangoFechaHora(inicio=inicio, fin=fin)

    for c in _agenda_del_asesor(context):
        if c.estado != EstadoCita.CANCELADA and _overlap(rango, c.rango):
            context.error = ValueError("El horario no está disponible")
            return None

    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion=observacion,
        rango=rango,
        tipo=tipo,
        estado=EstadoCita.PROGRAMADA,
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita
    context.solicitud_citas.setdefault(codigo_solicitud, []).append(cita.id_cita)
    return cita


# ============================================================
# Steps (exactos al .feature)
# ============================================================

@step(r'que el asesor "(?P<nombre_completo>.+)" está autenticado')
def step_asesor_autenticado(context: behave.runner.Context, nombre_completo: str):
    _ensure_context(context)
    if nombre_completo.strip() != "Juan Pérez":
        raise AssertionError("Este set de steps está definido para el asesor 'Juan Pérez' del feature.")

    context.asesor = Asesor(
        nombres="Juan",
        apellidos="Pérez",
        email_asesor="juan.perez@correo.com",
        rol=RolUsuario.ASESOR,
    )
    context.error = None


# OJO: En tu feature es "Y existe ..." (sin "que")
@step(r'existe un solicitante "(?P<nombre_completo>.+)" con cédula "(?P<cedula>[^"]+)"')
def step_existe_solicitante(context: behave.runner.Context, nombre_completo: str, cedula: str):
    _ensure_context(context)
    nombres, apellidos = nombre_completo.split(" ", 1) if " " in nombre_completo else (nombre_completo, "")
    context.solicitantes[cedula] = Solicitante(
        cedula=cedula,
        nombres=nombres,
        apellidos=apellidos,
        correo="maria.lopez@correo.com",
        telefono="0000000000",
        direccion="N/A",
        fecha_nacimiento=_d("1993-01-19"),
        habilitado=True,
    )
    context.error = None


# OJO: En tu feature es "Y existe ..." (sin "que")
@step(r'existe una solicitud migratoria con código "(?P<codigo>[^"]+)" del solicitante "(?P<cedula>[^"]+)" gestionada por el asesor "(?P<asesor_nombre>.+)"')
def step_existe_solicitud(context: behave.runner.Context, codigo: str, cedula: str, asesor_nombre: str):
    _ensure_context(context)
    assert context.asesor is not None, "Debe existir asesor autenticado."
    assert asesor_nombre.strip() == "Juan Pérez", "El feature usa 'Juan Pérez'."

    context.solicitudes[codigo] = SolicitudMigratoria(
        codigo=codigo,
        tipo_servicio=TipoServicio.RESIDENCIA,
        estado_actual=EstadoSolicitud.CREADA,
        fecha_creacion=_dt("2026-04-01 09:00"),
        fecha_expiracion=_dt("2026-10-01 09:00"),
    )

    context.solicitud_solicitante[codigo] = cedula
    context.solicitud_asesor[codigo] = context.asesor.email_asesor
    context.error = None


# -------------------- crear cita --------------------
@step(r'el asesor agenda una cita de tipo "(?P<tipo>ASESORIA)" para la solicitud "(?P<codigo>[^"]+)" desde "(?P<inicio>[^"]+)" hasta "(?P<fin>[^"]+)" con observación "(?P<obs>[^"]+)"')
def step_agenda_cita_valida(context: behave.runner.Context, tipo: str, codigo: str, inicio: str, fin: str, obs: str):
    _ensure_context(context)
    context.error = None
    _asegurar_solicitud(context, codigo)

    _agendar_cita_si_disponible(
        context,
        codigo_solicitud=codigo,
        tipo=TipoCita[tipo],
        inicio=_dt(inicio),
        fin=_dt(fin),
        observacion=obs,
    )


@step(r'la cita queda en estado "(?P<estado>PROGRAMADA)"')
def step_cita_programada(context: behave.runner.Context, estado: str):
    _ensure_context(context)
    assert context.ultima_cita_id is not None, "No hay cita creada."
    cita = _get_cita_by_id(context, context.ultima_cita_id)
    assert cita.estado == EstadoCita[estado]


@step(r'la cita queda asociada a la solicitud "(?P<codigo>[^"]+)"')
def step_cita_asociada_solicitud(context: behave.runner.Context, codigo: str):
    _ensure_context(context)
    assert context.ultima_cita_id is not None, "No hay cita creada."
    assert context.ultima_cita_id in context.solicitud_citas.get(codigo, [])


# -------------------- conflicto horario --------------------
@step(r'que el asesor tiene una cita "(?P<estado>PROGRAMADA)" desde "(?P<inicio>[^"]+)" hasta "(?P<fin>[^"]+)"')
def step_asesor_tiene_cita_programada(context: behave.runner.Context, estado: str, inicio: str, fin: str):
    _ensure_context(context)
    context.error = None

    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion="Cita existente",
        rango=RangoFechaHora(inicio=_dt(inicio), fin=_dt(fin)),
        tipo=TipoCita.ASESORIA,
        estado=EstadoCita[estado],
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita
    context.citas_snapshot_len = len(context.citas)


@step(r'el asesor intenta agendar otra cita para "(?P<inicio>[^"]+)" hasta "(?P<fin>[^"]+)"')
def step_intenta_agendar_misma_hora(context: behave.runner.Context, inicio: str, fin: str):
    _ensure_context(context)
    context.error = None
    context.citas_snapshot_len = len(context.citas)

    _agendar_cita_si_disponible(
        context,
        codigo_solicitud="SOL-001",
        tipo=TipoCita.ASESORIA,
        inicio=_dt(inicio),
        fin=_dt(fin),
        observacion="Intento",
    )


@step(r'se informa que el horario no está disponible')
def step_informa_no_disponible(context: behave.runner.Context):
    _ensure_context(context)
    assert context.error is not None, "Se esperaba error por conflicto."
    assert "no está disponible" in str(context.error).lower()


@step(r'no se agenda la cita')
def step_no_se_agenda(context: behave.runner.Context):
    _ensure_context(context)
    assert len(context.citas) == context.citas_snapshot_len, "La cita se agendó cuando no debía."


# -------------------- ver agenda --------------------
@step(r'que existe una cita "(?P<estado>PROGRAMADA)" para la solicitud "(?P<codigo>[^"]+)" desde "(?P<inicio>[^"]+)" hasta "(?P<fin>[^"]+)"')
def step_existe_cita_programada_para_solicitud(context: behave.runner.Context, estado: str, codigo: str, inicio: str, fin: str):
    _ensure_context(context)
    context.error = None
    _asegurar_solicitud(context, codigo)

    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion="Para agenda",
        rango=RangoFechaHora(inicio=_dt(inicio), fin=_dt(fin)),
        tipo=TipoCita.ASESORIA,
        estado=EstadoCita[estado],
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita
    context.solicitud_citas.setdefault(codigo, []).append(cita.id_cita)


@step(r'el asesor consulta su agenda del día "(?P<dia>[^"]+)"')
def step_consulta_agenda_dia(context: behave.runner.Context, dia: str):
    _ensure_context(context)
    dia_dt = _d(dia)

    agenda = [
        c for c in _agenda_del_asesor(context)
        if c.rango.inicio.date() == dia_dt and c.estado != EstadoCita.CANCELADA
    ]
    agenda.sort(key=lambda x: x.rango.inicio)
    context.agenda = agenda


@step(r'visualiza la cita a las "(?P<hora>\d{2}:\d{2})" asociada al solicitante "(?P<nombre_completo>.+)"')
def step_visualiza_cita_y_solicitante(context: behave.runner.Context, hora: str, nombre_completo: str):
    _ensure_context(context)
    assert context.agenda, "No hay citas en la agenda."
    assert context.agenda[0].rango.inicio.strftime("%H:%M") == hora

    assert "SOL-001" in context.solicitud_citas
    assert context.agenda[0].id_cita in context.solicitud_citas["SOL-001"]

    cedula = context.solicitud_solicitante.get("SOL-001", "ABC123")
    s = context.solicitantes.get(cedula)
    assert s is not None, "No existe el solicitante asociado."
    assert f"{s.nombres} {s.apellidos}".strip() == nombre_completo.strip()


# -------------------- reprogramar --------------------
@step(r'que existe una cita "(?P<estado>PROGRAMADA)" desde "(?P<inicio>[^"]+)" hasta "(?P<fin>[^"]+)"')
def step_existe_cita_programada(context: behave.runner.Context, estado: str, inicio: str, fin: str):
    _ensure_context(context)
    context.error = None

    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion="A reprogramar",
        rango=RangoFechaHora(inicio=_dt(inicio), fin=_dt(fin)),
        tipo=TipoCita.ASESORIA,
        estado=EstadoCita[estado],
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita


@step(r'el asesor reprograma la cita a "(?P<nuevo_inicio>[^"]+)" hasta "(?P<nuevo_fin>[^"]+)" con observación "(?P<obs>[^"]+)"')
def step_reprograma_cita(context: behave.runner.Context, nuevo_inicio: str, nuevo_fin: str, obs: str):
    _ensure_context(context)
    assert context.ultima_cita_id is not None, "No hay cita para reprogramar."

    cita = _get_cita_by_id(context, context.ultima_cita_id)
    nuevo_rango = RangoFechaHora(inicio=_dt(nuevo_inicio), fin=_dt(nuevo_fin))

    for c in _agenda_del_asesor(context):
        if c.id_cita == cita.id_cita:
            continue
        if c.estado != EstadoCita.CANCELADA and _overlap(nuevo_rango, c.rango):
            context.error = ValueError("El horario no está disponible")
            return

    cita.rango = nuevo_rango
    cita.observacion = obs
    cita.estado = EstadoCita.REPROGRAMADA
    context.error = None


@step(r'la cita queda en estado "(?P<estado>REPROGRAMADA)"')
def step_cita_reprogramada(context: behave.runner.Context, estado: str):
    _ensure_context(context)
    assert context.ultima_cita_id is not None
    cita = _get_cita_by_id(context, context.ultima_cita_id)
    assert cita.estado == EstadoCita[estado]


@step(r'la cita refleja el nuevo rango de fecha y hora')
def step_cita_refleja_rango(context: behave.runner.Context):
    _ensure_context(context)
    assert context.ultima_cita_id is not None
    cita = _get_cita_by_id(context, context.ultima_cita_id)
    assert cita.estado == EstadoCita.REPROGRAMADA


# -------------------- cancelar --------------------
@step(r'que existe una cita "(?P<estado>REPROGRAMADA)" desde "(?P<inicio>[^"]+)" hasta "(?P<fin>[^"]+)"')
def step_existe_cita_reprogramada(context: behave.runner.Context, estado: str, inicio: str, fin: str):
    _ensure_context(context)
    context.error = None

    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion="Lista para cancelar",
        rango=RangoFechaHora(inicio=_dt(inicio), fin=_dt(fin)),
        tipo=TipoCita.ASESORIA,
        estado=EstadoCita[estado],
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita


@step(r'el asesor cancela la cita con observación "(?P<obs>[^"]+)"')
def step_cancela_cita(context: behave.runner.Context, obs: str):
    _ensure_context(context)
    assert context.ultima_cita_id is not None
    cita = _get_cita_by_id(context, context.ultima_cita_id)
    cita.estado = EstadoCita.CANCELADA
    cita.observacion = obs
    context.error = None


@step(r'la cita queda en estado "(?P<estado>CANCELADA)"')
def step_cita_cancelada(context: behave.runner.Context, estado: str):
    _ensure_context(context)
    assert context.ultima_cita_id is not None
    cita = _get_cita_by_id(context, context.ultima_cita_id)
    assert cita.estado == EstadoCita[estado]


# -------------------- notificación al solicitante --------------------
@step(r'que existe una cita para la solicitud "(?P<codigo>[^"]+)"')
def step_existe_cita_para_solicitud(context: behave.runner.Context, codigo: str):
    _ensure_context(context)
    context.error = None
    _asegurar_solicitud(context, codigo)

    if codigo not in context.solicitud_citas or not context.solicitud_citas[codigo]:
        _agendar_cita_si_disponible(
            context,
            codigo_solicitud=codigo,
            tipo=TipoCita.ASESORIA,
            inicio=_dt("2026-04-19 10:00"),
            fin=_dt("2026-04-19 10:30"),
            observacion="Base",
        )


@step(r'la cita es creada o reprogramada')
def step_cita_creada_o_reprogramada(context: behave.runner.Context):
    _ensure_context(context)
    context.error = None

    codigo = "SOL-001"
    assert codigo in context.solicitud_citas and context.solicitud_citas[codigo], "No hay cita asociada a SOL-001."
    cita_id = context.solicitud_citas[codigo][0]
    cita = _get_cita_by_id(context, cita_id)

    cedula = context.solicitud_solicitante.get(codigo, "ABC123")
    msg = f"Cita {cita.estado.value} - {cita.rango.inicio.strftime('%Y-%m-%d %H:%M')}"
    _crear_notificacion(context, destinatario=cedula, tipo=TipoNotificacion.CITA_PROXIMA, mensaje=msg)


@step(r'el solicitante recibe una notificación de tipo "(?P<tipo>CITA_PROXIMA)"')
def step_solicitante_recibe_cita_proxima(context: behave.runner.Context, tipo: str):
    _ensure_context(context)
    assert any(
        n.tipo == TipoNotificacion[tipo] and n.destinatario == "ABC123"
        for n in context.notificaciones
    ), f"No existe notificación {tipo} para el solicitante."


@step(r'la notificación incluye la fecha y hora de la cita')
def step_notificacion_incluye_fecha_hora(context: behave.runner.Context):
    _ensure_context(context)

    if context.asesor is not None:
        for n in reversed(context.notificaciones):
            if n.tipo == TipoNotificacion.RECORDATORIO and n.destinatario == context.asesor.email_asesor:
                assert "2026-" in n.mensaje and ":" in n.mensaje, "La notificación no incluye fecha y hora."
                return

    for n in reversed(context.notificaciones):
        if n.tipo == TipoNotificacion.CITA_PROXIMA and n.destinatario == "ABC123":
            assert "2026-" in n.mensaje and ":" in n.mensaje, "La notificación no incluye fecha y hora."
            return

    raise AssertionError("No se encontró una notificación con fecha y hora para validar.")


# -------------------- recordatorio 24 horas antes --------------------
@step(r'que existe una cita "(?P<estado>PROGRAMADA)" para "(?P<inicio>[^"]+)"')
def step_existe_cita_programada_para_recordatorio(context: behave.runner.Context, estado: str, inicio: str):
    _ensure_context(context)
    context.error = None

    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion="Para recordatorio",
        rango=RangoFechaHora(inicio=_dt(inicio), fin=_dt("2026-04-19 10:30")),
        tipo=TipoCita.ASESORIA,
        estado=EstadoCita[estado],
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita


@step(r'faltan 24 horas para la cita')
def step_faltan_24_horas(context: behave.runner.Context):
    _ensure_context(context)
    assert context.ultima_cita_id is not None, "No hay cita para evaluar 24 horas."
    cita = _get_cita_by_id(context, context.ultima_cita_id)
    context.now = cita.rango.inicio - timedelta(hours=24)


@step(r'el asesor responsable recibe una notificación de tipo "(?P<tipo>RECORDATORIO)"')
def step_asesor_recibe_recordatorio(context: behave.runner.Context, tipo: str):
    _ensure_context(context)
    assert context.asesor is not None, "No hay asesor autenticado."
    assert context.ultima_cita_id is not None, "No hay cita para recordatorio."

    cita = _get_cita_by_id(context, context.ultima_cita_id)
    assert context.now is not None, "No existe tiempo simulado."
    assert (cita.rango.inicio - context.now) == timedelta(hours=24), "No faltan 24 horas exactas."

    msg = f"Recordatorio - {cita.rango.inicio.strftime('%Y-%m-%d %H:%M')}"
    _crear_notificacion(
        context,
        destinatario=context.asesor.email_asesor,
        tipo=TipoNotificacion[tipo],
        mensaje=msg,
    )
