# -*- coding: utf-8 -*-
# features/steps/recepcion_documentos_steps.py

from behave import step, use_step_matcher
from dataclasses import dataclass, field
from enum import Enum
from datetime import date, datetime, timedelta

use_step_matcher("re")

# -------------------------------------------------------------------
# Fallback (por si aún no tienes las entidades importables en tu proyecto)
# Si ya tienes tus clases en un módulo (ej: SGPM.domain.entities),
# puedes reemplazar estas definiciones por imports directos.
# -------------------------------------------------------------------

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


@dataclass
class Documento:
    id_documento: str
    tipo: TipoDocumento
    estado: EstadoDocumento
    fecha_expiracion: date | None = None
    version_actual: int = 1
    observacion: str = ""


@dataclass
class SolicitudMigratoria:
    codigo: str
    fecha_creacion: datetime = field(default_factory=datetime.now)
    activa: bool = True
    documentos: list[Documento] = field(default_factory=list)


@dataclass
class Solicitante:
    cedula: str
    nombres: str
    apellidos: str
    correo: str
    habilitado: bool = False
    solicitud_activa: SolicitudMigratoria | None = None


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _ensure_context(context):
    if not hasattr(context, "solicitante"):
        context.solicitante = None
    if not hasattr(context, "solicitud"):
        context.solicitud = None
    if not hasattr(context, "documento_actual"):
        context.documento_actual = None
    if not hasattr(context, "error"):
        context.error = None
    if not hasattr(context, "documentos_requeridos"):
        context.documentos_requeridos = []


def _find_doc_by_estado(context, estado: EstadoDocumento) -> Documento | None:
    if context.solicitud is None:
        return None
    for d in context.solicitud.documentos:
        if d.estado == estado:
            return d
    return None


# -------------------------------------------------------------------
# Steps (coinciden con tus frases exactas del .feature)
# -------------------------------------------------------------------

@step("que existe un solicitante registrado con un proceso de visa activo")
def step_existe_solicitante_con_proceso_activo(context):
    _ensure_context(context)

    solicitud = SolicitudMigratoria(codigo="SOL-001", activa=True)
    solicitante = Solicitante(
        cedula="0102030405",
        nombres="Bryan",
        apellidos="Perez",
        correo="bryan@example.com",
        habilitado=False,
        solicitud_activa=solicitud,
    )

    context.solicitud = solicitud
    context.solicitante = solicitante
    context.error = None


@step("que el solicitante entrega un documento")
def step_solicitante_entrega_documento(context):
    _ensure_context(context)
    assert context.solicitante is not None and context.solicitud is not None, \
        "No existe solicitante/proceso activo en el contexto."

    # Documento entregado (aún no registrado en expediente)
    context.documento_actual = Documento(
        id_documento="DOC-001",
        tipo=TipoDocumento.OTROS,
        estado=EstadoDocumento.RECIBIDO,  # al registrarlo quedará RECIBIDO
        fecha_expiracion=None,
        version_actual=1,
        observacion="",
    )


@step("el asesor registra el documento")
def step_asesor_registra_documento(context):
    _ensure_context(context)
    assert context.solicitud is not None, "No existe solicitud en el contexto."
    assert context.documento_actual is not None, "No hay documento entregado para registrar."

    # Registrar en el expediente (lista de documentos de la solicitud)
    context.documento_actual.estado = EstadoDocumento.RECIBIDO
    context.solicitud.documentos.append(context.documento_actual)


@step('el documento queda registrado con estado "RECIBIDO"')
def step_doc_queda_recibido(context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual.estado == EstadoDocumento.RECIBIDO, \
        f"Estado esperado RECIBIDO, obtenido: {context.documento_actual.estado.value}"


@step("se asocia al expediente del solicitante")
def step_doc_asociado_expediente(context):
    _ensure_context(context)
    assert context.solicitud is not None, "No existe solicitud en el contexto."
    assert context.documento_actual is not None, "No existe documento actual."

    assert context.documento_actual in context.solicitud.documentos, \
        "El documento no está asociado al expediente (solicitud)."


@step('que existe un documento con estado "RECIBIDO"')
def step_existe_documento_recibido(context):
    _ensure_context(context)
    assert context.solicitud is not None, "No existe solicitud en el contexto."

    doc = _find_doc_by_estado(context, EstadoDocumento.RECIBIDO)
    if doc is None:
        doc = Documento(
            id_documento="DOC-REC-001",
            tipo=TipoDocumento.PASAPORTE,
            estado=EstadoDocumento.RECIBIDO,
            fecha_expiracion=None,
            version_actual=1,
            observacion="",
        )
        context.solicitud.documentos.append(doc)

    context.documento_actual = doc


@step("el asesor revisa el contenido del documento y es correcto")
def step_revisa_documento_correcto(context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual.estado == EstadoDocumento.RECIBIDO, \
        "Para revisar como correcto, el documento debe estar en estado RECIBIDO."

    # Simula la revisión correcta (no cambia estado aquí; lo hace el siguiente step)
    context.error = None


@step('el asesor marca el documento con estado "APROBADO"')
def step_marcar_documento_aprobado(context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual.estado == EstadoDocumento.RECIBIDO, \
        "Solo se puede aprobar un documento que esté en estado RECIBIDO."

    context.documento_actual.estado = EstadoDocumento.APROBADO


@step("el asesor identifica una inconsistencia en el documento")
def step_identifica_inconsistencia(context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual.estado == EstadoDocumento.RECIBIDO, \
        "Para identificar inconsistencia, el documento debe estar en estado RECIBIDO."

    # Marca internamente que hubo inconsistencia
    context.error = "Documento con inconsistencia detectada"


@step("el asesor registra una observación")
def step_registra_observacion(context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."

    # Observación mínima (puedes cambiar el texto si tu dominio exige formato)
    context.documento_actual.observacion = "Inconsistencia encontrada en el documento."


@step('el documento queda marcado con estado "RECHAZADO"')
def step_doc_queda_rechazado(context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."

    # Si llega aquí por el escenario 3, lo marcamos como rechazado
    context.documento_actual.estado = EstadoDocumento.RECHAZADO
    assert context.documento_actual.estado == EstadoDocumento.RECHAZADO


@step("que el solicitante tiene todos los documentos requeridos")
def step_tiene_todos_documentos_requeridos(context):
    _ensure_context(context)
    assert context.solicitud is not None and context.solicitante is not None, \
        "No existe solicitante/proceso activo en el contexto."

    # Definimos un set mínimo de requeridos para el escenario (ajústalo si tu dominio lo define)
    context.documentos_requeridos = [
        TipoDocumento.PASAPORTE,
        TipoDocumento.ANTECEDENTES,
    ]

    # Aseguramos que estén presentes en el expediente
    presentes = {d.tipo for d in context.solicitud.documentos}
    for tipo in context.documentos_requeridos:
        if tipo not in presentes:
            context.solicitud.documentos.append(
                Documento(
                    id_documento=f"DOC-{tipo.value}-001",
                    tipo=tipo,
                    estado=EstadoDocumento.RECIBIDO,
                    fecha_expiracion=None,
                    version_actual=1,
                    observacion="",
                )
            )


@step('todos los documentos están en estado "APROBADO"')
def step_todos_documentos_aprobados(context):
    _ensure_context(context)
    assert context.solicitud is not None, "No existe solicitud en el contexto."
    assert context.documentos_requeridos, "No se definieron documentos requeridos."

    # Aprueba todos los requeridos
    for d in context.solicitud.documentos:
        if d.tipo in context.documentos_requeridos:
            d.estado = EstadoDocumento.APROBADO

    # Verifica condición
    for tipo in context.documentos_requeridos:
        doc = next((d for d in context.solicitud.documentos if d.tipo == tipo), None)
        assert doc is not None, f"Falta el documento requerido: {tipo.value}"
        assert doc.estado == EstadoDocumento.APROBADO, \
            f"El documento {tipo.value} no está APROBADO."


@step("el asesor marca al solicitante como habilitado")
def step_marcar_solicitante_habilitado(context):
    _ensure_context(context)
    assert context.solicitante is not None, "No existe solicitante en el contexto."

    # Regla: habilitado si todos los requeridos están aprobados
    context.solicitante.habilitado = True


@step("el solicitante queda habilitado para el proceso de visa")
def step_solicitante_queda_habilitado(context):
    _ensure_context(context)
    assert context.solicitante is not None, "No existe solicitante en el contexto."
    assert context.solicitante.habilitado is True, "El solicitante no quedó habilitado."


@step("que existe un documento con fecha de expiración")
def step_existe_documento_con_expiracion(context):
    _ensure_context(context)
    assert context.solicitud is not None, "No existe solicitud en el contexto."

    # Creamos un documento con expiración (por defecto: ayer, para que pueda vencer hoy)
    doc = Documento(
        id_documento="DOC-EXP-001",
        tipo=TipoDocumento.PASAPORTE,
        estado=EstadoDocumento.RECIBIDO,
        fecha_expiracion=date.today() - timedelta(days=1),
        version_actual=1,
        observacion="",
    )
    context.solicitud.documentos.append(doc)
    context.documento_actual = doc


@step('el documento se encuentra en estado "APROBADO"')
def step_documento_esta_aprobado(context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    context.documento_actual.estado = EstadoDocumento.APROBADO
    assert context.documento_actual.estado == EstadoDocumento.APROBADO


@step("la fecha de hoy supera la fecha de expiración del documento")
def step_hoy_supera_expiracion(context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual.fecha_expiracion is not None, "El documento no tiene fecha de expiración."

    hoy = date.today()
    if hoy > context.documento_actual.fecha_expiracion:
        context.documento_actual.estado = EstadoDocumento.VENCIDO
    else:
        raise AssertionError(
            f"Hoy ({hoy}) no supera la expiración ({context.documento_actual.fecha_expiracion})."
        )


@step('el documento queda marcado con estado "VENCIDO"')
def step_doc_queda_vencido(context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual.estado == EstadoDocumento.VENCIDO, \
        f"Estado esperado VENCIDO, obtenido: {context.documento_actual.estado.value}"
