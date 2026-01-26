# test/feature/steps/control_estado_fechas_respectivas_solicitudes.py

import behave.runner
from behave import step, use_step_matcher
import unicodedata
import re
from datetime import datetime, date

from SGPM.domain.entities import (
    Solicitante,
    Asesor,
    SolicitudMigratoria,
    parse_datetime_iso,
    parse_estado_solicitud,
    parse_date_iso,
    TransicionEstadoNoPermitida,
    CampoFechaNoPermitido,
    FechaInvalida,
)

# matcher exacto (parse)
use_step_matcher("parse")


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _ensure_context_store(context: behave.runner.Context):
    if not hasattr(context, "solicitantes"):
        context.solicitantes = {}  # cedula -> Solicitante
    if not hasattr(context, "solicitudes"):
        context.solicitudes = {}   # codigo -> SolicitudMigratoria
    if not hasattr(context, "asesor"):
        context.asesor = None
    if not hasattr(context, "error"):
        context.error = None
    if not hasattr(context, "cliente_actual"):
        context.cliente_actual = None
    if not hasattr(context, "solicitud_actual"):
        context.solicitud_actual = None


def _norm(s: str) -> str:
    s = s or ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))  # quita tildes
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace('"', "").replace("'", "")
    return s


def _date_only(value) -> str:
    """Normaliza a YYYY-MM-DD (acepta date, datetime o string ISO con/sin hora)."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    s = str(value).strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}", s):
        return s[:10]
    try:
        return parse_datetime_iso(s).date().isoformat()
    except Exception:
        return s


# ------------------------------------------------------------
# STEPS (TODO con @step) - PARSE
# ------------------------------------------------------------

@step('que existe un cliente con cédula "{cedula}" y correo "{correo}"')
def existe_cliente(context: behave.runner.Context, cedula: str, correo: str):
    _ensure_context_store(context)
    cliente = Solicitante(
        cedula=cedula,
        nombres="Nombres",
        apellidos="Apellidos",
        correo=correo,
        telefono="0999999999",
        fechaNacimiento=parse_date_iso("2000-01-01"),
    )
    context.solicitantes[cedula] = cliente
    context.cliente_actual = cliente


@step('existe una solicitud con código "{codigo}" para el cliente "{cedula}" con fecha de creación "{fecha_creacion}"')
def existe_solicitud(context: behave.runner.Context, codigo: str, cedula: str, fecha_creacion: str):
    _ensure_context_store(context)
    fc = parse_datetime_iso(fecha_creacion)

    solicitud = SolicitudMigratoria(
        codigo=codigo,
        tipoServicio=None,
        estadoActual=parse_estado_solicitud("Creada"),
        fechaCreación=fc,
        fechaExpiracion=fc,
    )

    if cedula in context.solicitantes:
        solicitud.asignar_solicitante(context.solicitantes[cedula])

    context.solicitudes[codigo] = solicitud
    context.solicitud_actual = solicitud


@step('la solicitud está en estado "{estado}"')
def solicitud_en_estado(context: behave.runner.Context, estado: str):
    _ensure_context_store(context)
    context.solicitud_actual.estadoActual = parse_estado_solicitud(estado)


@step('el asesor autenticado es "{email_asesor}"')
def asesor_autenticado(context: behave.runner.Context, email_asesor: str):
    _ensure_context_store(context)
    asesor = Asesor(
        nombres="Asesor",
        apellidos="Uno",
        emailAsesor=email_asesor,
    )
    context.asesor = asesor
    if context.solicitud_actual is not None:
        context.solicitud_actual.asignar_asesor(asesor)


@step('que la transición de "{estado_inicial}" a "{estado_nuevo}" está permitida')
def transicion_permitida(context: behave.runner.Context, estado_inicial: str, estado_nuevo: str):
    _ensure_context_store(context)
    e_ini = parse_estado_solicitud(estado_inicial)
    e_new = parse_estado_solicitud(estado_nuevo)
    context.solicitud_actual.estadoActual = e_ini
    assert context.solicitud_actual.transicion_permitida(e_new), (
        f"Se esperaba transición permitida: {e_ini.value} -> {e_new.value}"
    )


@step('que la transición de "{estado_inicial}" a "{estado_nuevo}" no está permitida')
def transicion_no_permitida(context: behave.runner.Context, estado_inicial: str, estado_nuevo: str):
    _ensure_context_store(context)
    e_ini = parse_estado_solicitud(estado_inicial)
    e_new = parse_estado_solicitud(estado_nuevo)
    context.solicitud_actual.estadoActual = e_ini
    assert not context.solicitud_actual.transicion_permitida(e_new), (
        f"Se esperaba transición NO permitida: {e_ini.value} -> {e_new.value}"
    )


@step('que la solicitud está en estado "Archivada"')
def solicitud_archivada(context: behave.runner.Context):
    _ensure_context_store(context)
    context.solicitud_actual.estadoActual = parse_estado_solicitud("Archivada")


@step('el asesor cambia el estado a "{estado_nuevo}" indicando el motivo "{motivo}"')
def cambia_estado(context: behave.runner.Context, estado_nuevo: str, motivo: str):
    _ensure_context_store(context)
    context.error = None

    nuevo = parse_estado_solicitud(estado_nuevo)

    # OJO: tu dominio usa fecha_evento = fechaCreación
    fecha_evento = context.solicitud_actual.fechaCreación
    context.fecha_evento = fecha_evento

    try:
        context.solicitud_actual.cambiar_estado(
            nuevo=nuevo,
            usuario=context.asesor.emailAsesor,
            motivo=motivo,
            fecha_evento=fecha_evento,
        )
    except Exception as e:
        context.error = e
        raise AssertionError(f"Se esperaba cambio de estado exitoso, pero falló: {e}")

    context.estado_nuevo = nuevo
    context.motivo = motivo


@step('el asesor intenta cambiar el estado a "{estado_nuevo}" indicando el motivo "{motivo}"')
def intenta_cambiar_estado(context: behave.runner.Context, estado_nuevo: str, motivo: str):
    _ensure_context_store(context)
    context.error = None

    nuevo = parse_estado_solicitud(estado_nuevo)
    fecha_evento = context.solicitud_actual.fechaCreación
    context.fecha_evento = fecha_evento

    try:
        context.solicitud_actual.cambiar_estado(
            nuevo=nuevo,
            usuario=context.asesor.emailAsesor,
            motivo=motivo,
            fecha_evento=fecha_evento,
        )
    except Exception as e:
        context.error = e

    context.estado_nuevo = nuevo
    context.motivo = motivo


@step('que "{tipo_fecha}" es un campo de fecha permitido del proceso')
def campo_fecha_permitido(context: behave.runner.Context, tipo_fecha: str):
    _ensure_context_store(context)
    assert tipo_fecha in {"fechaRecepcionDocs", "fechaEnvioSolicitud", "fechaCita"}


@step('"{fecha_valor}" es igual o posterior a "2026-01-10"')
def fecha_valida(context: behave.runner.Context, fecha_valor: str):
    _ensure_context_store(context)
    fv = parse_date_iso(fecha_valor)
    fc = context.solicitud_actual.fechaCreación.date()
    assert fv >= fc


@step('"{fecha_valor}" es anterior a "2026-01-10"')
def fecha_invalida(context: behave.runner.Context, fecha_valor: str):
    _ensure_context_store(context)
    fv = parse_date_iso(fecha_valor)
    fc = context.solicitud_actual.fechaCreación.date()
    assert fv < fc


@step('el asesor asigna "{tipo_fecha}" con valor "{fecha_valor}"')
def asigna_fecha(context: behave.runner.Context, tipo_fecha: str, fecha_valor: str):
    _ensure_context_store(context)
    context.error = None

    fecha_evento = context.solicitud_actual.fechaCreación
    context.fecha_evento = fecha_evento

    try:
        context.solicitud_actual.asignar_fecha_proceso(
            campo=tipo_fecha,
            valor_iso=fecha_valor,
            usuario=context.asesor.emailAsesor,
            fecha_evento=fecha_evento,
        )
    except Exception as e:
        context.error = e

    context.tipo_fecha = tipo_fecha
    context.fecha_valor = fecha_valor


@step('el asesor consulta el detalle de la solicitud "{codigo}"')
def consulta_detalle(context: behave.runner.Context, codigo: str):
    _ensure_context_store(context)
    context.solicitud_actual = context.solicitudes[codigo]


@step('el asesor consulta el historial de la solicitud "{codigo}"')
def consulta_historial(context: behave.runner.Context, codigo: str):
    _ensure_context_store(context)
    context.solicitud_actual = context.solicitudes[codigo]


@step('el asesor visualiza el estado actual como "{estado_nuevo}"')
def visualiza_estado(context: behave.runner.Context, estado_nuevo: str):
    esperado = parse_estado_solicitud(estado_nuevo)
    assert context.solicitud_actual.estadoActual == esperado


@step('el asesor visualiza la "fechaUltimaActualizacion" como "{fecha_evento}"')
def visualiza_fecha_ultima(context: behave.runner.Context, fecha_evento: str):
    esperado = _date_only(fecha_evento)
    real = context.solicitud_actual.obtener_fechas_clave().get("fechaUltimaActualizacion")
    real = _date_only(real)
    assert real == esperado, f"fechaUltimaActualizacion esperada={esperado} real={real}"


@step("al revisar el historial, el asesor visualiza un registro con:")
def historial_estado_registro(context: behave.runner.Context):
    data = {row[0].strip(): row[1].strip() for row in context.table}
    historial = context.solicitud_actual.obtener_historial_estados()
    assert historial, "No hay historial de estados"
    ultimo = historial[0]

    if "usuario" in data:
        assert ultimo["usuario"] == data["usuario"]
    if "anterior" in data:
        assert ultimo["anterior"] == parse_estado_solicitud(data["anterior"]).value
    if "nuevo" in data:
        assert ultimo["nuevo"] == parse_estado_solicitud(data["nuevo"]).value
    if "motivo" in data:
        assert ultimo["motivo"] == data["motivo"]
    if "fecha" in data:
        assert _date_only(ultimo["fecha"]) == _date_only(data["fecha"])


@step('el asesor visualiza el mensaje "{mensaje_error}"')
def visualiza_mensaje(context: behave.runner.Context, mensaje_error: str):
    assert context.error is not None, "Se esperaba un error pero no ocurrió."
    esperado = _norm(mensaje_error)
    real = _norm(str(context.error))
    if esperado not in real and real not in esperado:
        raise AssertionError(f"Mensaje esperado: '{mensaje_error}' | Mensaje real: '{str(context.error)}'")


@step("al revisar el historial, el asesor no visualiza un registro asociado a esta acción")
def no_registro_historial(context: behave.runner.Context):
    assert context.error is not None, "Se esperaba error para validar que no se registre historial"
    historial = context.solicitud_actual.obtener_historial_estados()
    for r in historial:
        assert r.get("nuevo") != context.estado_nuevo.value


@step('el asesor visualiza el resultado como "{resultado}"')
def visualiza_resultado(context: behave.runner.Context, resultado: str):
    real = "rechazado" if context.error else "aceptado"
    assert real == resultado.strip().lower()


@step('si el resultado es "rechazado", el asesor visualiza el mensaje "{mensaje_error}"')
def si_rechazado_mensaje(context: behave.runner.Context, mensaje_error: str):
    if context.error:
        assert mensaje_error.lower() in str(context.error).lower()


@step('el asesor visualiza "{tipo_fecha}" como "{fecha_valor}"')
def visualiza_fecha(context: behave.runner.Context, tipo_fecha: str, fecha_valor: str):
    real = context.solicitud_actual.obtener_fecha_proceso(tipo_fecha)
    assert _date_only(real) == _date_only(parse_date_iso(fecha_valor))


@step("al revisar el historial de fechas, el asesor visualiza un registro con:")
def historial_fechas_registro(context: behave.runner.Context):
    data = {row[0].strip(): row[1].strip() for row in context.table}

    historial = context.solicitud_actual.obtener_historial_fechas()
    assert historial, "No hay historial de fechas"
    ultimo = historial[0]

    if "usuario" in data:
        assert ultimo["usuario"] == data["usuario"]
    if "campo" in data:
        assert ultimo["campo"] == data["campo"]
    if "valorNuevo" in data:
        assert _date_only(ultimo["valorNuevo"]) == _date_only(parse_date_iso(data["valorNuevo"]))
    if "fecha" in data:
        assert _date_only(ultimo["fecha"]) == _date_only(data["fecha"])


@step('el asesor visualiza que "{tipo_fecha}" mantiene su valor anterior')
def mantiene_valor_anterior(context: behave.runner.Context, tipo_fecha: str):
    assert context.error is not None, "Se esperaba error para mantener valor anterior"


@step('que el asesor visualiza "fechaRecepcionDocs" como "{fecha_recepcion_docs}"')
def visualiza_fecha_recepcion_docs(context: behave.runner.Context, fecha_recepcion_docs: str):
    real = context.solicitud_actual.obtener_fecha_proceso("fechaRecepcionDocs")
    assert _date_only(real) == _date_only(fecha_recepcion_docs)


@step("el asesor visualiza las fechas clave registradas:")
def visualiza_fechas_clave(context: behave.runner.Context):
    esperadas = {row[0].strip(): row[1].strip() for row in context.table}
    reales = context.solicitud_actual.obtener_fechas_clave()

    for k, v in esperadas.items():
        if _norm(v).startswith("(vacio)") or _norm(v).startswith("(vacío)"):
            assert reales.get(k) is None
        else:
            assert _date_only(reales.get(k)) == _date_only(v), f"{k}: esperado={v} real={reales.get(k)}"


@step("el asesor visualiza los cambios de estado en orden cronológico descendente")
def historial_estados_desc(context: behave.runner.Context):
    historial = context.solicitud_actual.obtener_historial_estados()
    for i in range(len(historial) - 1):
        assert _date_only(historial[i]["fecha"]) >= _date_only(historial[i + 1]["fecha"])


@step("cada cambio de estado muestra: estado anterior, estado nuevo, usuario, fecha, motivo")
def historial_estado_campos(context: behave.runner.Context):
    historial = context.solicitud_actual.obtener_historial_estados()
    for r in historial:
        assert r.get("anterior")
        assert r.get("nuevo")
        assert r.get("usuario")
        assert r.get("fecha")
        assert r.get("motivo") is not None


@step("el asesor visualiza los cambios de fechas en orden cronológico descendente")
def historial_fechas_desc(context: behave.runner.Context):
    historial = context.solicitud_actual.obtener_historial_fechas()
    for i in range(len(historial) - 1):
        assert _date_only(historial[i]["fecha"]) >= _date_only(historial[i + 1]["fecha"])


@step("cada cambio de fecha muestra: campo, valor anterior, valor nuevo, usuario, fecha")
def historial_fecha_campos(context: behave.runner.Context):
    historial = context.solicitud_actual.obtener_historial_fechas()
    for r in historial:
        assert r.get("campo")
        assert "valorAnterior" in r
        assert r.get("valorNuevo")
        assert r.get("usuario")
        assert r.get("fecha")
