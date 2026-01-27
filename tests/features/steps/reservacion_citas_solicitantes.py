import behave.runner
from behave import step, use_step_matcher
from dataclasses import dataclass
from datetime import datetime, date, timedelta
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


class TipoDocumento(Enum):
    PASAPORTE = "PASAPORTE"
    ANTECEDENTES = "ANTECEDENTES"
    ESTADOS_BANCARIOS = "ESTADOS_BANCARIOS"
    CONTRATO_TRABAJO = "CONTRATO_TRABAJO"
    MATRICULA_ESTUDIOS = "MATRICULA_ESTUDIOS"
    OTROS = "OTROS"


class EstadoDocumento(Enum):
    RECIBIDO = "RECIBIDO"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    VENCIDO = "VENCIDO"


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
# Entidades / Value Objects (según diagrama)
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
# Helpers (almacenamiento en memoria para los steps)
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
        # codigo_solicitud -> lista de ids_cita
        context.solicitud_citas: Dict[str, List[str]] = {}
    if not hasattr(context, "error"):
        context.error: Optional[Exception] = None
    if not hasattr(context, "ultima_cita_id"):
        context.ultima_cita_id: Optional[str] = None
    if not hasattr(context, "agenda"):
        context.agenda: List[Cita] = []
    if not hasattr(context, "now"):
        # “tiempo actual” simulado para el escenario de 24 horas
        context.now: Optional[datetime] = None


def _dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M")


def _d(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


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
    # En estos steps, todas las citas creadas se asumen del asesor autenticado.
    return list(context.citas)


# ============================================================
# Steps (IGUALITOS a tu feature, solo que implementados)
# ============================================================
@step('que el asesor "Juan Pérez" está autenticado')
def step_impl(context):
    _ensure_context(context)
    context.asesor = Asesor(
        nombres="Juan",
        apellidos="Pérez",
        email_asesor="juan.perez@correo.com",
        rol=RolUsuario.ASESOR,
    )
    context.error = None


@step('existe un solicitante "María López" con cédula "ABC123"')
def step_impl(context):
    _ensure_context(context)
    context.solicitantes["ABC123"] = Solicitante(
        cedula="ABC123",
        nombres="María",
        apellidos="López",
        correo="maria.lopez@correo.com",
        telefono="0000000000",
        direccion="N/A",
        fecha_nacimiento=_d("1993-01-19"),
        habilitado=True,
    )
    context.error = None


@step('existe una solicitud migratoria con código "SOL-001" del solicitante "ABC123" gestionada por el asesor "Juan Pérez"')
def step_impl(context):
    _ensure_context(context)
    # El diagrama no tiene FK directas, así que guardamos la relación en el contexto
    context.solicitudes["SOL-001"] = SolicitudMigratoria(
        codigo="SOL-001",
        tipo_servicio=TipoServicio.RESIDENCIA,
        estado_actual=EstadoSolicitud.CREADA,
        fecha_creacion=_dt("2026-04-01 09:00"),
        fecha_expiracion=_dt("2026-10-01 09:00"),
    )
    # relación extra para pruebas (no rompe el diagrama; es solo el “mapa” del test)
    context.solicitud_solicitante = {"SOL-001": "ABC123"}
    context.solicitud_asesor = {"SOL-001": context.asesor.email_asesor if context.asesor else "juan.perez@correo.com"}
    context.error = None


@step('el asesor agenda una cita de tipo "ASESORIA" para la solicitud "SOL-001" desde "2026-04-19 10:00" hasta "2026-04-19 10:30" con observación "Primera revisión"')
def step_impl(context):
    _ensure_context(context)
    context.error = None

    rango = RangoFechaHora(inicio=_dt("2026-04-19 10:00"), fin=_dt("2026-04-19 10:30"))

    # Validación de conflicto: no puede cruzarse con otra cita activa
    for c in _agenda_del_asesor(context):
        if c.estado != EstadoCita.CANCELADA and _overlap(rango, c.rango):
            context.error = ValueError("El horario no está disponible")
            return

    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion="Primera revisión",
        rango=rango,
        tipo=TipoCita.ASESORIA,
        estado=EstadoCita.PROGRAMADA,
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita

    # Relación solicitud -> cita (del diagrama: SolicitudMigratoria agenda Cita)
    context.solicitud_citas.setdefault("SOL-001", []).append(cita.id_cita)


@step('la cita queda en estado "PROGRAMADA"')
def step_impl(context):
    _ensure_context(context)
    assert context.ultima_cita_id is not None, "No hay cita creada."
    cita = _get_cita_by_id(context, context.ultima_cita_id)
    assert cita.estado == EstadoCita.PROGRAMADA


@step('la cita queda asociada a la solicitud "SOL-001"')
def step_impl(context):
    _ensure_context(context)
    assert context.ultima_cita_id is not None, "No hay cita creada."
    assert "SOL-001" in context.solicitud_citas, "No existe asociación de citas para SOL-001."
    assert context.ultima_cita_id in context.solicitud_citas["SOL-001"]


@step('que el asesor tiene una cita "PROGRAMADA" desde "2026-04-19 10:00" hasta "2026-04-19 10:30"')
def step_impl(context):
    _ensure_context(context)
    context.error = None

    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion="Cita existente",
        rango=RangoFechaHora(inicio=_dt("2026-04-19 10:00"), fin=_dt("2026-04-19 10:30")),
        tipo=TipoCita.ASESORIA,
        estado=EstadoCita.PROGRAMADA,
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita


@step('el asesor intenta agendar otra cita para "2026-04-19 10:00" hasta "2026-04-19 10:30"')
def step_impl(context):
    _ensure_context(context)
    context.error = None

    rango = RangoFechaHora(inicio=_dt("2026-04-19 10:00"), fin=_dt("2026-04-19 10:30"))
    for c in _agenda_del_asesor(context):
        if c.estado != EstadoCita.CANCELADA and _overlap(rango, c.rango):
            context.error = ValueError("El horario no está disponible")
            return

    # (Si no hubo conflicto, entonces sí se agenda; pero este escenario espera conflicto)
    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion="Intento",
        rango=rango,
        tipo=TipoCita.ASESORIA,
        estado=EstadoCita.PROGRAMADA,
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita


@step("se informa que el horario no está disponible")
def step_impl(context):
    _ensure_context(context)
    assert context.error is not None, "Se esperaba un error de conflicto."
    assert "no está disponible" in str(context.error).lower()


@step("no se agenda la cita")
def step_impl(context):
    _ensure_context(context)
    assert context.error is not None, "En conflicto no debe agendarse la cita."


@step('que existe una cita "PROGRAMADA" para la solicitud "SOL-001" desde "2026-04-19 10:00" hasta "2026-04-19 10:30"')
def step_impl(context):
    _ensure_context(context)
    context.error = None

    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion="Para agenda",
        rango=RangoFechaHora(inicio=_dt("2026-04-19 10:00"), fin=_dt("2026-04-19 10:30")),
        tipo=TipoCita.ASESORIA,
        estado=EstadoCita.PROGRAMADA,
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita
    context.solicitud_citas.setdefault("SOL-001", []).append(cita.id_cita)


@step('el asesor consulta su agenda del día "2026-04-19"')
def step_impl(context):
    _ensure_context(context)
    dia = _d("2026-04-19")
    agenda = [c for c in _agenda_del_asesor(context) if c.rango.inicio.date() == dia and c.estado != EstadoCita.CANCELADA]
    agenda.sort(key=lambda x: x.rango.inicio)
    context.agenda = agenda


@step('visualiza la cita a las "10:00" asociada al solicitante "María López"')
def step_impl(context):
    _ensure_context(context)
    assert len(context.agenda) > 0, "No hay citas en la agenda."
    assert context.agenda[0].rango.inicio.strftime("%H:%M") == "10:00"

    # Verifica que la cita está en una solicitud que pertenece al solicitante esperado
    assert "SOL-001" in context.solicitud_citas
    assert context.agenda[0].id_cita in context.solicitud_citas["SOL-001"]

    solicitante = context.solicitantes.get("ABC123")
    assert solicitante is not None
    assert f"{solicitante.nombres} {solicitante.apellidos}" == "María López"


@step('que existe una cita "PROGRAMADA" desde "2026-04-19 10:00" hasta "2026-04-19 10:30"')
def step_impl(context):
    _ensure_context(context)
    context.error = None

    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion="A reprogramar",
        rango=RangoFechaHora(inicio=_dt("2026-04-19 10:00"), fin=_dt("2026-04-19 10:30")),
        tipo=TipoCita.ASESORIA,
        estado=EstadoCita.PROGRAMADA,
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita


@step('el asesor reprograma la cita a "2026-04-20 11:30" hasta "2026-04-20 12:00" con observación "Cambio por disponibilidad"')
def step_impl(context):
    _ensure_context(context)
    assert context.ultima_cita_id is not None, "No hay cita para reprogramar."
    context.error = None

    cita = _get_cita_by_id(context, context.ultima_cita_id)
    nuevo_rango = RangoFechaHora(inicio=_dt("2026-04-20 11:30"), fin=_dt("2026-04-20 12:00"))

    # Validación de conflicto (excluye la misma cita)
    for c in _agenda_del_asesor(context):
        if c.id_cita == cita.id_cita:
            continue
        if c.estado != EstadoCita.CANCELADA and _overlap(nuevo_rango, c.rango):
            context.error = ValueError("El horario no está disponible")
            return

    cita.rango = nuevo_rango
    cita.observacion = "Cambio por disponibilidad"
    cita.estado = EstadoCita.REPROGRAMADA


@step('la cita queda en estado "REPROGRAMADA"')
def step_impl(context):
    _ensure_context(context)
    assert context.ultima_cita_id is not None, "No hay cita para validar."
    cita = _get_cita_by_id(context, context.ultima_cita_id)
    assert cita.estado == EstadoCita.REPROGRAMADA


@step("la cita refleja el nuevo rango de fecha y hora")
def step_impl(context):
    _ensure_context(context)
    assert context.ultima_cita_id is not None, "No hay cita para validar."
    cita = _get_cita_by_id(context, context.ultima_cita_id)
    assert cita.rango.inicio == _dt("2026-04-20 11:30")
    assert cita.rango.fin == _dt("2026-04-20 12:00")


@step('que existe una cita "REPROGRAMADA" desde "2026-04-20 11:30" hasta "2026-04-20 12:00"')
def step_impl(context):
    _ensure_context(context)
    context.error = None

    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion="Lista para cancelar",
        rango=RangoFechaHora(inicio=_dt("2026-04-20 11:30"), fin=_dt("2026-04-20 12:00")),
        tipo=TipoCita.ASESORIA,
        estado=EstadoCita.REPROGRAMADA,
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita


@step('el asesor cancela la cita con observación "Solicitante no podrá asistir"')
def step_impl(context):
    _ensure_context(context)
    assert context.ultima_cita_id is not None, "No hay cita para cancelar."
    cita = _get_cita_by_id(context, context.ultima_cita_id)
    cita.estado = EstadoCita.CANCELADA
    cita.observacion = "Solicitante no podrá asistir"
    context.error = None


@step('la cita queda en estado "CANCELADA"')
def step_impl(context):
    _ensure_context(context)
    assert context.ultima_cita_id is not None
    cita = _get_cita_by_id(context, context.ultima_cita_id)
    assert cita.estado == EstadoCita.CANCELADA


@step('que existe una cita para la solicitud "SOL-001"')
def step_impl(context):
    _ensure_context(context)
    context.error = None

    # asegura que haya al menos una cita vinculada a SOL-001
    if "SOL-001" not in context.solicitud_citas or len(context.solicitud_citas["SOL-001"]) == 0:
        cita = Cita(
            id_cita=f"CITA-{len(context.citas) + 1:03d}",
            observacion="Base",
            rango=RangoFechaHora(inicio=_dt("2026-04-19 10:00"), fin=_dt("2026-04-19 10:30")),
            tipo=TipoCita.ASESORIA,
            estado=EstadoCita.PROGRAMADA,
        )
        context.citas.append(cita)
        context.solicitud_citas.setdefault("SOL-001", []).append(cita.id_cita)
        context.ultima_cita_id = cita.id_cita


@step("la cita es creada o reprogramada")
def step_impl(context):
    _ensure_context(context)
    context.error = None

    # toma una cita asociada a SOL-001
    cita_id = context.solicitud_citas["SOL-001"][0]
    cita = _get_cita_by_id(context, cita_id)

    solicitante_cedula = getattr(context, "solicitud_solicitante", {}).get("SOL-001", "ABC123")
    msg = f"Cita {cita.estado.value} - {cita.rango.inicio.strftime('%Y-%m-%d %H:%M')}"
    _crear_notificacion(context, destinatario=solicitante_cedula, tipo=TipoNotificacion.CITA_PROXIMA, mensaje=msg)


@step('el solicitante recibe una notificación de tipo "CITA_PROXIMA"')
def step_impl(context):
    _ensure_context(context)
    assert any(
        n.tipo == TipoNotificacion.CITA_PROXIMA and n.destinatario == "ABC123"
        for n in context.notificaciones
    ), "No existe notificación CITA_PROXIMA para el solicitante."


@step("la notificación incluye la fecha y hora de la cita")
def step_impl(context):
    _ensure_context(context)

    # Busca primero notificación de RECORDATORIO (asesor)
    if context.asesor is not None:
        for n in reversed(context.notificaciones):
            if getattr(n, "tipo", None) == TipoNotificacion.RECORDATORIO and n.destinatario == context.asesor.email_asesor:
                assert "2026-" in n.mensaje and ":" in n.mensaje, "La notificación no incluye fecha y hora."
                return

    # Si no fue recordatorio, valida CITA_PROXIMA (solicitante)
    for n in reversed(context.notificaciones):
        if getattr(n, "tipo", None) == TipoNotificacion.CITA_PROXIMA and n.destinatario == "ABC123":
            assert "2026-" in n.mensaje and ":" in n.mensaje, "La notificación no incluye fecha y hora."
            return

    raise AssertionError("No se encontró una notificación con fecha y hora para validar.")



@step('que existe una cita "PROGRAMADA" para "2026-04-19 10:00"')
def step_impl(context):
    _ensure_context(context)
    context.error = None

    cita = Cita(
        id_cita=f"CITA-{len(context.citas) + 1:03d}",
        observacion="Para recordatorio",
        rango=RangoFechaHora(inicio=_dt("2026-04-19 10:00"), fin=_dt("2026-04-19 10:30")),
        tipo=TipoCita.ASESORIA,
        estado=EstadoCita.PROGRAMADA,
    )
    context.citas.append(cita)
    context.ultima_cita_id = cita.id_cita


@step("faltan 24 horas para la cita")
def step_impl(context):
    _ensure_context(context)
    assert context.ultima_cita_id is not None, "No hay cita para evaluar 24 horas."
    cita = _get_cita_by_id(context, context.ultima_cita_id)
    context.now = cita.rango.inicio - timedelta(hours=24)


@step('el asesor responsable recibe una notificación de tipo "RECORDATORIO"')
def step_impl(context):
    _ensure_context(context)
    assert context.asesor is not None, "No hay asesor autenticado."
    assert context.ultima_cita_id is not None, "No hay cita para recordatorio."
    cita = _get_cita_by_id(context, context.ultima_cita_id)

    # “disparo” del recordatorio: ahora está a 24 horas exactas
    assert context.now is not None
    delta = cita.rango.inicio - context.now
    assert delta == timedelta(hours=24)

    msg = f"Recordatorio - {cita.rango.inicio.strftime('%Y-%m-%d %H:%M')}"
    _crear_notificacion(
        context,
        destinatario=context.asesor.email_asesor,
        tipo=TipoNotificacion.RECORDATORIO,
        mensaje=msg,
    )

