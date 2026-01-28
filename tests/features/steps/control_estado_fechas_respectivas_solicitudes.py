# -*- coding: utf-8 -*-
# features/steps/control_estado_fechas_solicitud_steps.py

from behave import step, use_step_matcher
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, date

use_step_matcher("re")

# ============================================================
# Enums (alineados al diagrama + feature)
# ============================================================

class EstadoSolicitud(Enum):
    CREADA = "CREADA"
    EN_REVISION = "EN_REVISION"
    DOCUMENTOS_PENDIENTES = "DOCUMENTOS_PENDIENTES"
    ENVIADA = "ENVIADA"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    CERRADA = "CERRADA"
    ARCHIVADA = "ARCHIVADA"


class TipoServicio(Enum):
    VISA_TURISMO = "VISA_TURISMO"
    VISA_TRABAJO = "VISA_TRABAJO"
    ESTUDIOS = "ESTUDIOS"
    RESIDENCIA = "RESIDENCIA"


# ============================================================
# Clases de dominio (completas según diagrama)
# ============================================================

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
    rol: str


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

def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def ensure_context(context):
    if not hasattr(context, "solicitante"):
        context.solicitante = None
    if not hasattr(context, "asesor"):
        context.asesor = None
    if not hasattr(context, "solicitud"):
        context.solicitud = None

    if not hasattr(context, "transiciones"):
        context.transiciones = {}

    if not hasattr(context, "fechas_clave"):
        context.fechas_clave = {
            "fechaRecepcionDocs": None,
            "fechaEnvioSolicitud": None,
            "fechaCita": None,
        }

    if not hasattr(context, "fecha_ultima_actualizacion"):
        context.fecha_ultima_actualizacion = None

    if not hasattr(context, "historial_estados"):
        context.historial_estados = []

    if not hasattr(context, "historial_fechas"):
        context.historial_fechas = []

    if not hasattr(context, "ultimo_resultado"):
        context.ultimo_resultado = None

    if not hasattr(context, "ultimo_mensaje"):
        context.ultimo_mensaje = None


# ============================================================
# Antecedentes
# ============================================================

@step(r'que existe un solicitante con los siguientes datos:')
def step_crear_solicitante(context):
    ensure_context(context)
    row = context.table[0]
    context.solicitante = Solicitante(
        cedula=row["cedula"],
        nombres=row["nombres"],
        apellidos=row["apellidos"],
        correo=row["correo"],
        telefono=row["telefono"],
        direccion=row["direccion"],
        fecha_nacimiento=parse_date(row["fecha_nacimiento"]),
        habilitado=row["habilitado"].lower() == "true",
    )


@step(r'que existe un asesor con los siguientes datos:')
def step_crear_asesor(context):
    ensure_context(context)
    row = context.table[0]
    context.asesor = Asesor(
        nombres=row["nombres"],
        apellidos=row["apellidos"],
        email_asesor=row["email_asesor"],
        rol=row["rol"],
    )


@step(r'que existe una solicitud migratoria con los siguientes datos:')
def step_crear_solicitud(context):
    ensure_context(context)
    row = context.table[0]
    context.solicitud = SolicitudMigratoria(
        codigo=row["codigo"],
        tipo_servicio=TipoServicio[row["tipo_servicio"]],
        estado_actual=EstadoSolicitud[row["estado_actual"]],
        fecha_creacion=datetime.strptime(row["fecha_creacion"], "%Y-%m-%d"),
        fecha_expiracion=datetime.strptime(row["fecha_expiracion"], "%Y-%m-%d"),
    )
    context.fecha_ultima_actualizacion = context.solicitud.fecha_creacion.date()


@step(r'el asesor se encuentra autenticado en el sistema')
def step_asesor_autenticado(context):
    ensure_context(context)
    assert context.asesor is not None


# ============================================================
# Transiciones de estado
# ============================================================

@step(r'que la transición de "(.*)" a "(.*)" está permitida')
def step_transicion_permitida(context, estado_inicial, estado_nuevo):
    ensure_context(context)
    context.transiciones[(estado_inicial, estado_nuevo)] = True


@step(r'que la transición de "(.*)" a "(.*)" no está permitida')
def step_transicion_no_permitida(context, estado_inicial, estado_nuevo):
    ensure_context(context)
    context.transiciones[(estado_inicial, estado_nuevo)] = False


@step(r'la solicitud ".*" se encuentra en estado "(.*)"')
def step_set_estado(context, estado):
    ensure_context(context)
    context.solicitud.estado_actual = EstadoSolicitud[estado]


@step(r'el asesor cambia el estado de la solicitud con los siguientes datos:')
def step_cambiar_estado(context):
    ensure_context(context)
    row = context.table[0]
    nuevo_estado = EstadoSolicitud[row["nuevo_estado"]]
    motivo = row["motivo"]

    actual = context.solicitud.estado_actual

    if actual == EstadoSolicitud.ARCHIVADA:
        context.ultimo_resultado = "rechazado"
        context.ultimo_mensaje = "No se permiten cambios en Archivada"
        return

    if nuevo_estado == EstadoSolicitud.RECHAZADA and motivo.strip() == "":
        context.ultimo_resultado = "rechazado"
        context.ultimo_mensaje = "El motivo es obligatorio al rechazar"
        return

    permitido = context.transiciones.get((actual.name, nuevo_estado.name), False)
    if not permitido:
        context.ultimo_resultado = "rechazado"
        context.ultimo_mensaje = "No se permite la transición solicitada"
        return

    context.solicitud.estado_actual = nuevo_estado
    context.historial_estados.append({
        "usuario": context.asesor.email_asesor,
        "estado_anterior": actual.name,
        "estado_nuevo": nuevo_estado.name,
        "fecha": context.fecha_ultima_actualizacion.strftime("%Y-%m-%d"),
        "motivo": motivo,
    })

    context.ultimo_resultado = "aceptado"
    context.ultimo_mensaje = None


# ============================================================
# Fechas clave
# ============================================================

@step(r'el asesor asigna la fecha con los siguientes datos:')
def step_asignar_fecha(context):
    ensure_context(context)
    row = context.table[0]
    campo = row["campo"]
    valor = parse_date(row["valor"])

    creacion = context.solicitud.fecha_creacion.date()

    if valor < creacion:
        context.ultimo_resultado = "rechazado"
        context.ultimo_mensaje = "La fecha no puede ser anterior a la fecha de creación"
        return

    if campo == "fechaEnvioSolicitud":
        frd = context.fechas_clave["fechaRecepcionDocs"]
        if frd and valor < frd:
            context.ultimo_resultado = "rechazado"
            context.ultimo_mensaje = "La fecha de envío no puede ser anterior a la recepción de documentos"
            return

    anterior = context.fechas_clave[campo]
    context.fechas_clave[campo] = valor

    context.historial_fechas.append({
        "usuario": context.asesor.email_asesor,
        "campo": campo,
        "valorAnterior": anterior.strftime("%Y-%m-%d") if anterior else "(vacío)",
        "valorNuevo": valor.strftime("%Y-%m-%d"),
        "fecha": context.fecha_ultima_actualizacion.strftime("%Y-%m-%d"),
    })

    context.ultimo_resultado = "aceptado"
    context.ultimo_mensaje = None


# ============================================================
# Consultas
# ============================================================

@step(r'el asesor consulta el detalle de la solicitud ".*"')
def step_consultar_detalle(context):
    ensure_context(context)
    assert context.solicitud is not None


@step(r'el asesor consulta el historial de la solicitud ".*"')
def step_consultar_historial(context):
    ensure_context(context)
    assert context.solicitud is not None
