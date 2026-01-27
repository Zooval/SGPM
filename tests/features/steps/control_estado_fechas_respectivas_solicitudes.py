# -*- coding: utf-8 -*-
# features/steps/control_estado_fechas_solicitud_steps.py

from behave import step, use_step_matcher
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, date
from typing import Optional, Dict, Any, List, Tuple

use_step_matcher("re")


# ============================================================
# Enums (según diagrama + ARCHIVADA porque tu feature la usa)
# ============================================================
class EstadoSolicitud(Enum):
    CREADA = "Creada"
    EN_REVISION = "En revision"
    DOCUMENTOS_PENDIENTES = "Documentos pendientes"
    ENVIADA = "Enviada"
    APROBADA = "Aprobada"
    RECHAZADA = "Rechazada"
    CERRADA = "Cerrada"
    ARCHIVADA = "Archivada"  # requerido por tu feature


class TipoServicio(Enum):
    VISA_TURISMO = "VISA_TURISMO"
    VISA_TRABAJO = "VISA_TRABAJO"
    ESTUDIOS = "ESTUDIOS"
    RESIDENCIA = "RESIDENCIA"


# ============================================================
# Clases mínimas alineadas al diagrama para esta feature
# (Solicitante, Asesor, SolicitudMigratoria)
# ============================================================
@dataclass
class Solicitante:
    cedula: str
    nombres: str = ""
    apellidos: str = ""
    correo: str = ""
    telefono: str = ""
    direccion: str = ""
    fecha_nacimiento: Optional[date] = None
    habilitado: bool = False


@dataclass
class Asesor:
    nombres: str = ""
    apellidos: str = ""
    email_asesor: str = ""


@dataclass
class SolicitudMigratoria:
    codigo: str
    tipo_servicio: TipoServicio
    estado_actual: EstadoSolicitud
    fecha_creacion: datetime
    fecha_expiracion: datetime


# ============================================================
# Helpers
# ============================================================
def parse_date_iso(s: str) -> date:
    return datetime.strptime(s.strip(), "%Y-%m-%d").date()


def parse_datetime_from_feature_date(s: str) -> datetime:
    # feature trae YYYY-MM-DD -> lo convertimos a datetime 00:00:00
    d = parse_date_iso(s)
    return datetime(d.year, d.month, d.day, 0, 0, 0)


def fmt_date(d: Optional[date]) -> str:
    return "(vacío)" if d is None else d.strftime("%Y-%m-%d")


def fmt_datetime_as_date(dt: datetime) -> str:
    return dt.date().strftime("%Y-%m-%d")


def _ensure_context(context):
    if not hasattr(context, "cliente"):
        context.cliente = None  # Solicitante
    if not hasattr(context, "asesor"):
        context.asesor = None  # Asesor
    if not hasattr(context, "solicitud"):
        context.solicitud = None  # SolicitudMigratoria

    # reglas de transición: (estado_inicial_str, estado_nuevo_str) -> bool
    if not hasattr(context, "transiciones"):
        context.transiciones = {}

    # resultado/mensaje
    if not hasattr(context, "ultimo_resultado"):
        context.ultimo_resultado = None  # "aceptado" / "rechazado"
    if not hasattr(context, "ultimo_mensaje"):
        context.ultimo_mensaje = None

    # "fechas clave" del proceso (NO están en clase del diagrama, se guardan en contexto)
    if not hasattr(context, "fechas_clave"):
        context.fechas_clave = {
            "fechaRecepcionDocs": None,
            "fechaEnvioSolicitud": None,
            "fechaCita": None,
        }  # campo -> Optional[date]

    # fechaUltimaActualizacion (en feature)
    if not hasattr(context, "fecha_ultima_actualizacion"):
        context.fecha_ultima_actualizacion = None  # date

    # historiales (NO están en diagrama, soporte para la feature)
    if not hasattr(context, "historial_estados"):
        context.historial_estados = []  # List[Dict[str, Any]]
    if not hasattr(context, "historial_fechas"):
        context.historial_fechas = []  # List[Dict[str, Any]]

    # snapshots para asserts "no se registra"
    if not hasattr(context, "historial_estados_snapshot_len"):
        context.historial_estados_snapshot_len = 0
    if not hasattr(context, "historial_fechas_snapshot_len"):
        context.historial_fechas_snapshot_len = 0
    if not hasattr(context, "fechas_snapshot"):
        context.fechas_snapshot = {}  # campo -> Optional[date]


def _estado_from_feature(texto: str) -> EstadoSolicitud:
    t = texto.strip()
    for e in EstadoSolicitud:
        if e.value.lower() == t.lower():
            return e
    raise AssertionError(f"EstadoSolicitud no reconocido en feature: '{texto}'")


def _campo_fecha_permitido(campo: str) -> bool:
    return campo in {"fechaRecepcionDocs", "fechaEnvioSolicitud", "fechaCita"}


def _get_fecha_clave(context, campo: str) -> Optional[date]:
    _ensure_context(context)

    if campo == "fechaCreacion":
        assert context.solicitud is not None, "Solicitud no existe."
        return context.solicitud.fecha_creacion.date()

    if campo == "fechaUltimaActualizacion":
        return context.fecha_ultima_actualizacion

    return context.fechas_clave.get(campo)


def _set_fecha_clave(context, campo: str, valor: Optional[date]):
    _ensure_context(context)
    context.fechas_clave[campo] = valor


def _registrar_historial_estado(context, anterior: EstadoSolicitud, nuevo: EstadoSolicitud, motivo: str, fecha_evento: date):
    _ensure_context(context)
    context.historial_estados.append({
        "usuario": context.asesor.email_asesor,
        "anterior": anterior.value,
        "nuevo": nuevo.value,
        "fecha": fecha_evento.strftime("%Y-%m-%d"),
        "motivo": motivo,
    })


def _registrar_historial_fecha(context, campo: str, anterior: Optional[date], nuevo: Optional[date], fecha_evento: date):
    _ensure_context(context)
    context.historial_fechas.append({
        "usuario": context.asesor.email_asesor,
        "campo": campo,
        "valorAnterior": fmt_date(anterior),
        "valorNuevo": fmt_date(nuevo),
        "fecha": fecha_evento.strftime("%Y-%m-%d"),
    })


def _aplicar_cambio_estado(context, estado_nuevo_str: str, motivo: str):
    _ensure_context(context)
    assert context.solicitud is not None, "No hay solicitud en contexto."
    assert context.asesor is not None, "No hay asesor autenticado."

    # Archivada bloquea todo
    if context.solicitud.estado_actual == EstadoSolicitud.ARCHIVADA:
        context.ultimo_resultado = "rechazado"
        context.ultimo_mensaje = "No se permiten cambios en Archivada"
        return

    nuevo = _estado_from_feature(estado_nuevo_str)
    anterior = context.solicitud.estado_actual

    # Regla: Rechazada exige motivo
    if nuevo == EstadoSolicitud.RECHAZADA and (motivo is None or motivo.strip() == ""):
        context.ultimo_resultado = "rechazado"
        context.ultimo_mensaje = "El motivo es obligatorio al rechazar"
        return

    permitido = context.transiciones.get((anterior.value, nuevo.value), False)
    if not permitido:
        context.ultimo_resultado = "rechazado"
        context.ultimo_mensaje = "No se permite la transición solicitada"
        return

    # Aplica cambio
    context.solicitud.estado_actual = nuevo

    # En tu feature: fecha_evento siempre se compara como YYYY-MM-DD
    # Tomamos como fecha_evento la "fechaUltimaActualizacion" actual (inicialmente = creación).
    fecha_evento = context.fecha_ultima_actualizacion
    if fecha_evento is None:
        fecha_evento = context.solicitud.fecha_creacion.date()

    context.fecha_ultima_actualizacion = fecha_evento
    _registrar_historial_estado(context, anterior, nuevo, motivo, fecha_evento)

    context.ultimo_resultado = "aceptado"
    context.ultimo_mensaje = None


def _aplicar_asignacion_fecha(context, tipo_fecha: str, fecha_valor: str):
    _ensure_context(context)
    assert context.solicitud is not None, "No hay solicitud en contexto."
    assert context.asesor is not None, "No hay asesor autenticado."

    if not _campo_fecha_permitido(tipo_fecha):
        context.ultimo_resultado = "rechazado"
        context.ultimo_mensaje = "Campo de fecha no permitido"
        return

    valor = parse_date_iso(fecha_valor)
    creacion = context.solicitud.fecha_creacion.date()

    anterior = _get_fecha_clave(context, tipo_fecha)

    # Bloquear anterior a creación
    if valor < creacion:
        context.ultimo_resultado = "rechazado"
        context.ultimo_mensaje = "La fecha no puede ser anterior a la fecha de creación"
        return

    # Coherencia: envio no puede ser anterior a recepcionDocs
    if tipo_fecha == "fechaEnvioSolicitud":
        frd = _get_fecha_clave(context, "fechaRecepcionDocs")
        if frd is not None and valor < frd:
            context.ultimo_resultado = "rechazado"
            context.ultimo_mensaje = "La fecha de envío no puede ser anterior a la recepción de documentos"
            return

    _set_fecha_clave(context, tipo_fecha, valor)

    # fecha_evento de tu feature (se compara con YYYY-MM-DD)
    fecha_evento = context.fecha_ultima_actualizacion
    if fecha_evento is None:
        fecha_evento = creacion

    context.fecha_ultima_actualizacion = fecha_evento
    _registrar_historial_fecha(context, tipo_fecha, anterior, valor, fecha_evento)

    context.ultimo_resultado = "aceptado"
    context.ultimo_mensaje = None


# ============================================================
# Steps - Antecedentes
# ============================================================
@step(r'que existe un cliente con cédula "0912345678" y correo "cliente@mail\.com"')
def step_existe_cliente(context):
    _ensure_context(context)
    context.cliente = Solicitante(cedula="0912345678", correo="cliente@mail.com")
    context.ultimo_resultado = None
    context.ultimo_mensaje = None


@step(r'existe una solicitud con código "SOL-2026-0001" para el cliente "0912345678" con fecha de creación "2026-01-10"')
def step_existe_solicitud(context):
    _ensure_context(context)
    assert context.cliente is not None, "Cliente no existe en contexto."

    fc_dt = parse_datetime_from_feature_date("2026-01-10")

    # En el diagrama existe fecha_expiracion (datetime); para el test basta una fecha futura.
    fe_dt = fc_dt.replace(day=fc_dt.day)  # base
    fe_dt = fe_dt.replace()  # no-op seguro

    # Expiración: + 30 días (sin imports extra)
    fe_dt = fc_dt + (datetime(2026, 2, 9) - datetime(2026, 1, 10))  # 30 días exactos

    context.solicitud = SolicitudMigratoria(
        codigo="SOL-2026-0001",
        tipo_servicio=TipoServicio.VISA_TURISMO,
        estado_actual=EstadoSolicitud.CREADA,
        fecha_creacion=fc_dt,
        fecha_expiracion=fe_dt,
    )

    # iniciales del feature
    context.fecha_ultima_actualizacion = fc_dt.date()
    context.fechas_clave = {"fechaRecepcionDocs": None, "fechaEnvioSolicitud": None, "fechaCita": None}
    context.historial_estados = []
    context.historial_fechas = []


@step(r'la solicitud está en estado "Creada"')
def step_estado_creada(context):
    _ensure_context(context)
    assert context.solicitud is not None, "Solicitud no existe."
    context.solicitud.estado_actual = EstadoSolicitud.CREADA


@step(r'el asesor autenticado es "asesor@agencia\.com"')
def step_asesor_autenticado(context):
    _ensure_context(context)
    context.asesor = Asesor(email_asesor="asesor@agencia.com")


# ============================================================
# Steps - Transiciones permitidas / no permitidas
# ============================================================
@step(r'que la transición de "(?P<estado_inicial>.+)" a "(?P<estado_nuevo>.+)" está permitida')
def step_transicion_permitida(context, estado_inicial, estado_nuevo):
    _ensure_context(context)
    context.transiciones[(estado_inicial.strip(), estado_nuevo.strip())] = True


@step(r'que la transición de "(?P<estado_inicial>.+)" a "(?P<estado_nuevo>.+)" no está permitida')
def step_transicion_no_permitida(context, estado_inicial, estado_nuevo):
    _ensure_context(context)
    context.transiciones[(estado_inicial.strip(), estado_nuevo.strip())] = False


@step(r'la solicitud está en estado "(?P<estado_inicial>.+)"')
def step_set_estado_inicial(context, estado_inicial):
    _ensure_context(context)
    assert context.solicitud is not None, "Solicitud no existe."
    context.solicitud.estado_actual = _estado_from_feature(estado_inicial)


@step(r'el asesor cambia el estado a "(?P<estado_nuevo>.+)" indicando el motivo "(?P<motivo>.*)"')
def step_cambia_estado(context, estado_nuevo, motivo):
    _ensure_context(context)
    context.historial_estados_snapshot_len = len(context.historial_estados)
    _aplicar_cambio_estado(context, estado_nuevo, motivo)


@step(r'el asesor intenta cambiar el estado a "(?P<estado_nuevo>.+)" indicando el motivo "(?P<motivo>.*)"')
def step_intenta_cambiar_estado(context, estado_nuevo, motivo):
    _ensure_context(context)
    context.historial_estados_snapshot_len = len(context.historial_estados)
    _aplicar_cambio_estado(context, estado_nuevo, motivo)


@step(r'el asesor visualiza el estado actual como "(?P<estado_esperado>.+)"')
def step_visualiza_estado_actual(context, estado_esperado):
    _ensure_context(context)
    assert context.solicitud is not None, "Solicitud no existe."
    actual = context.solicitud.estado_actual.value
    assert actual.lower() == estado_esperado.strip().lower(), f"Estado actual '{actual}' != '{estado_esperado}'"


@step(r'el asesor visualiza la "fechaUltimaActualizacion" como "(?P<fecha_evento>.+)"')
def step_visualiza_fecha_ultima_actualizacion(context, fecha_evento):
    _ensure_context(context)
    assert context.fecha_ultima_actualizacion is not None, "fechaUltimaActualizacion no está inicializada."
    actual = context.fecha_ultima_actualizacion.strftime("%Y-%m-%d")
    assert actual == fecha_evento.strip(), f"fechaUltimaActualizacion '{actual}' != '{fecha_evento}'"


@step(r'el asesor visualiza el mensaje "(?P<mensaje_error>.+)"')
def step_visualiza_mensaje(context, mensaje_error):
    _ensure_context(context)
    assert context.ultimo_mensaje is not None, "No hay mensaje de error en el contexto."
    assert context.ultimo_mensaje.strip().lower() == mensaje_error.strip().lower(), \
        f"Mensaje '{context.ultimo_mensaje}' != '{mensaje_error}'"


@step(r"al revisar el historial, el asesor visualiza un registro con:")
def step_historial_contiene_registro(context):
    _ensure_context(context)
    assert len(context.historial_estados) > 0, "No hay registros en historial de estados."
    ultimo = context.historial_estados[-1]
    expected = {row[0].strip(): row[1].strip() for row in context.table}

    for k, v in expected.items():
        assert k in ultimo, f"El historial no contiene la clave '{k}'"
        assert str(ultimo[k]).strip().lower() == v.strip().lower(), f"Historial[{k}]='{ultimo[k]}' != '{v}'"


@step(r"al revisar el historial, el asesor no visualiza un registro asociado a esta acción")
def step_historial_no_nuevo_registro(context):
    _ensure_context(context)
    assert len(context.historial_estados) == context.historial_estados_snapshot_len, \
        "Se registró un cambio en historial cuando NO debía."


@step(r'el asesor visualiza el resultado como "(?P<resultado>.+)"')
def step_visualiza_resultado(context, resultado):
    _ensure_context(context)
    assert context.ultimo_resultado is not None, "No hay resultado en el contexto."
    assert context.ultimo_resultado.strip().lower() == resultado.strip().lower(), \
        f"Resultado '{context.ultimo_resultado}' != '{resultado}'"


@step(r'si el resultado es "rechazado", el asesor visualiza el mensaje "(?P<mensaje_error>.*)"')
def step_si_rechazado_muestra_mensaje(context, mensaje_error):
    _ensure_context(context)
    if (context.ultimo_resultado or "").strip().lower() == "rechazado":
        assert context.ultimo_mensaje is not None, "Se esperaba mensaje de error pero no existe."
        assert context.ultimo_mensaje.strip().lower() == mensaje_error.strip().lower(), \
            f"Mensaje '{context.ultimo_mensaje}' != '{mensaje_error}'"


@step(r'que la solicitud está en estado "Archivada"')
def step_solicitud_archivada(context):
    _ensure_context(context)
    assert context.solicitud is not None, "Solicitud no existe."
    context.solicitud.estado_actual = EstadoSolicitud.ARCHIVADA


# ============================================================
# Steps - Fechas clave
# ============================================================
@step(r'que "(?P<tipo_fecha>.+)" es un campo de fecha permitido del proceso')
def step_campo_fecha_permitido(context, tipo_fecha):
    _ensure_context(context)
    assert _campo_fecha_permitido(tipo_fecha.strip()), f"Campo '{tipo_fecha}' no es permitido."


@step(r'"(?P<fecha_valor>.+)" es igual o posterior a "2026-01-10"')
def step_fecha_igual_o_posterior(context, fecha_valor):
    v = parse_date_iso(fecha_valor)
    base = parse_date_iso("2026-01-10")
    assert v >= base, f"La fecha '{fecha_valor}' no es igual/posterior a 2026-01-10"


@step(r'"(?P<fecha_valor>.+)" es anterior a "2026-01-10"')
def step_fecha_anterior(context, fecha_valor):
    v = parse_date_iso(fecha_valor)
    base = parse_date_iso("2026-01-10")
    assert v < base, f"La fecha '{fecha_valor}' no es anterior a 2026-01-10"


@step(r'el asesor asigna "(?P<tipo_fecha>.+)" con valor "(?P<fecha_valor>.+)"')
def step_asignar_fecha(context, tipo_fecha, fecha_valor):
    _ensure_context(context)
    campo = tipo_fecha.strip()

    context.fechas_snapshot[campo] = _get_fecha_clave(context, campo)
    context.historial_fechas_snapshot_len = len(context.historial_fechas)

    _aplicar_asignacion_fecha(context, campo, fecha_valor)


@step(r'el asesor visualiza "(?P<tipo_fecha>.+)" como "(?P<fecha_valor>.+)"')
def step_visualiza_fecha_campo(context, tipo_fecha, fecha_valor):
    _ensure_context(context)
    actual = _get_fecha_clave(context, tipo_fecha.strip())
    assert actual is not None, f"El campo '{tipo_fecha}' no tiene valor."
    assert actual.strftime("%Y-%m-%d") == fecha_valor.strip(), f"{tipo_fecha}='{actual}' != '{fecha_valor}'"


@step(r"al revisar el historial de fechas, el asesor visualiza un registro con:")
def step_historial_fechas_contiene_registro(context):
    _ensure_context(context)
    assert len(context.historial_fechas) > 0, "No hay registros en historial de fechas."
    ultimo = context.historial_fechas[-1]
    expected = {row[0].strip(): row[1].strip() for row in context.table}

    for k, v in expected.items():
        assert k in ultimo, f"El historial de fechas no contiene la clave '{k}'"
        assert str(ultimo[k]).strip().lower() == v.strip().lower(), f"HistorialFechas[{k}]='{ultimo[k]}' != '{v}'"


@step(r'el asesor visualiza que "(?P<tipo_fecha>.+)" mantiene su valor anterior')
def step_mantiene_valor_anterior(context, tipo_fecha):
    _ensure_context(context)
    campo = tipo_fecha.strip()
    anterior = context.fechas_snapshot.get(campo)
    actual = _get_fecha_clave(context, campo)
    assert anterior == actual, f"El campo '{campo}' cambió cuando no debía."


@step(r'que el asesor visualiza "fechaRecepcionDocs" como "(?P<fecha_recepcion_docs>.+)"')
def step_visualiza_fecha_recepcion_docs(context, fecha_recepcion_docs):
    _ensure_context(context)
    if fecha_recepcion_docs.strip() == "(vacío)":
        _set_fecha_clave(context, "fechaRecepcionDocs", None)
    else:
        _set_fecha_clave(context, "fechaRecepcionDocs", parse_date_iso(fecha_recepcion_docs))


# ============================================================
# Steps - Consulta detalle
# ============================================================
@step(r'el asesor consulta el detalle de la solicitud "SOL-2026-0001"')
def step_consulta_detalle(context):
    _ensure_context(context)
    assert context.solicitud is not None, "Solicitud no existe."
    assert context.solicitud.codigo == "SOL-2026-0001", "Código de solicitud no coincide."


@step(r"el asesor visualiza las fechas clave registradas:")
def step_visualiza_fechas_clave_registradas(context):
    _ensure_context(context)
    for row in context.table:
        campo = row[0].strip()
        esperado = row[1].strip()

        val = _get_fecha_clave(context, campo)
        if esperado == "(vacío)":
            assert val is None, f"Se esperaba {campo} vacío, pero fue {val}"
        else:
            assert val is not None, f"Se esperaba {campo}='{esperado}' pero está vacío"
            assert val.strftime("%Y-%m-%d") == esperado, f"{campo}='{val}' != '{esperado}'"


# ============================================================
# Steps - Consulta historial
# ============================================================
@step(r'el asesor consulta el historial de la solicitud "SOL-2026-0001"')
def step_consulta_historial(context):
    _ensure_context(context)
    assert context.solicitud is not None, "Solicitud no existe."
    assert context.solicitud.codigo == "SOL-2026-0001", "Código de solicitud no coincide."


@step(r"el asesor visualiza los cambios de estado en orden cronológico descendente")
def step_cambios_estado_desc(context):
    _ensure_context(context)
    fechas = [h["fecha"] for h in context.historial_estados]
    assert fechas == sorted(fechas, reverse=True), "El historial de estados no está en orden descendente."


@step(r"cada cambio de estado muestra: estado anterior, estado nuevo, usuario, fecha, motivo")
def step_cambio_estado_campos(context):
    _ensure_context(context)
    for h in context.historial_estados:
        for k in ("anterior", "nuevo", "usuario", "fecha", "motivo"):
            assert k in h and str(h[k]).strip() != "", f"Falta campo '{k}' en historial de estados."


@step(r"el asesor visualiza los cambios de fechas en orden cronológico descendente")
def step_cambios_fechas_desc(context):
    _ensure_context(context)
    fechas = [h["fecha"] for h in context.historial_fechas]
    assert fechas == sorted(fechas, reverse=True), "El historial de fechas no está en orden descendente."


@step(r"cada cambio de fecha muestra: campo, valor anterior, valor nuevo, usuario, fecha")
def step_cambio_fecha_campos(context):
    _ensure_context(context)
    for h in context.historial_fechas:
        for k in ("campo", "valorAnterior", "valorNuevo", "usuario", "fecha"):
            assert k in h and str(h[k]).strip() != "", f"Falta campo '{k}' en historial de fechas."
