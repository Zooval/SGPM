# -*- coding: utf-8 -*-
# features/steps/recepcion_documentos_steps.py

import behave.runner
from behave import step, use_step_matcher
from datetime import date, datetime, timedelta
from SGPM.domain.enums import *
from SGPM.domain.entities import *

use_step_matcher("re")


# ============================================================
# Helpers de contexto (relaciones en memoria)
# ============================================================
def _ensure_context(context: behave.runner.Context):
    if not hasattr(context, "solicitante"):
        context.solicitante = None  # Solicitante actual
    if not hasattr(context, "solicitud_activa"):
        context.solicitud_activa = None  # SolicitudMigratoria actual (en curso)
    if not hasattr(context, "documento_actual"):
        context.documento_actual = None  # Documento en operación
    if not hasattr(context, "error"):
        context.error = None

    # Relaciones (diagrama):
    # Solicitante "1" o-- "0..*" Documento : posee
    if not hasattr(context, "documentos_por_solicitante"):
        context.documentos_por_solicitante = {}  # cedula -> list[Documento]

    # Solicitante "1" o-- "0..*" SolicitudMigratoria : crea
    if not hasattr(context, "solicitudes_por_solicitante"):
        context.solicitudes_por_solicitante = {}  # cedula -> list[SolicitudMigratoria]

    # para requeridos en criterio 4
    if not hasattr(context, "documentos_requeridos"):
        context.documentos_requeridos = []  # list[TipoDocumento]


def _docs_of_current(context) -> list:
    _ensure_context(context)
    assert context.solicitante is not None, "No existe solicitante en el contexto."
    return context.documentos_por_solicitante.setdefault(context.solicitante.cedula, [])


def _find_doc_by_estado(context, estado: EstadoDocumento) -> Documento | None:
    for d in _docs_of_current(context):
        if d.estado == estado:
            return d
    return None


def _find_doc_by_tipo(context, tipo: TipoDocumento) -> Documento | None:
    for d in _docs_of_current(context):
        if d.tipo == tipo:
            return d
    return None


# ============================================================
# Steps (coinciden con tu .feature)
# ============================================================
@step(r"que existe un solicitante registrado con un proceso de visa activo")
def step_existe_solicitante_con_proceso_activo(context: behave.runner.Context):
    _ensure_context(context)

    solicitante = Solicitante(
        cedula="0102030405",
        nombres="Bryan",
        apellidos="Perez",
        correo="bryan@example.com",
        telefono="0999999999",
        direccion="Av. Principal 123",
        fecha_nacimiento=date(1998, 5, 12),
        habilitado=False,
    )

    # Solicitud migratoria (proceso activo) -> lo modelamos como "no cerrada"
    ahora = datetime.now()
    solicitud = SolicitudMigratoria(
        codigo="SOL-001",
        tipo_servicio=TipoServicio.VISA_TURISMO,
        estado_actual=EstadoSolicitud.DOCUMENTOS_PENDIENTES,
        fecha_creacion=ahora,
        fecha_expiracion=ahora + timedelta(days=60),
    )

    context.solicitante = solicitante
    context.solicitud_activa = solicitud

    context.documentos_por_solicitante.setdefault(solicitante.cedula, [])
    context.solicitudes_por_solicitante.setdefault(solicitante.cedula, []).append(solicitud)

    context.documento_actual = None
    context.error = None


# --------------------- Criterio 1 ---------------------
@step(r"que el solicitante entrega un documento")
def step_solicitante_entrega_documento(context: behave.runner.Context):
    _ensure_context(context)
    assert context.solicitante is not None and context.solicitud_activa is not None, \
        "No existe solicitante o proceso de visa activo."

    # Se crea el documento "entregado" (aún no asociado al expediente).
    # Al registrarlo, quedará en estado RECIBIDO.
    context.documento_actual = Documento(
        id_documento="DOC-001",
        tipo=TipoDocumento.OTROS,
        estado=EstadoDocumento.RECIBIDO,
        fecha_expiracion=date.today() + timedelta(days=365),  # por defecto: válido 1 año
        version_actual=1,
        observacion="",
    )


@step(r"el asesor registra el documento")
def step_asesor_registra_documento(context: behave.runner.Context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No hay documento entregado para registrar."

    # Registrar => se asocia al solicitante (expediente) y queda RECIBIDO
    context.documento_actual.estado = EstadoDocumento.RECIBIDO
    _docs_of_current(context).append(context.documento_actual)


@step(r'el documento queda registrado con estado "RECIBIDO"')
def step_doc_queda_recibido(context: behave.runner.Context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual.estado == EstadoDocumento.RECIBIDO, \
        f"Se esperaba RECIBIDO, pero fue {context.documento_actual.estado.value}"


@step(r"se asocia al expediente del solicitante")
def step_doc_asociado_expediente(context: behave.runner.Context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual in _docs_of_current(context), \
        "El documento no fue asociado al expediente del solicitante."


# --------------------- Criterio 2 ---------------------
@step(r'que existe un documento con estado "RECIBIDO"')
def step_existe_documento_recibido(context: behave.runner.Context):
    _ensure_context(context)

    doc = _find_doc_by_estado(context, EstadoDocumento.RECIBIDO)
    if doc is None:
        doc = Documento(
            id_documento="DOC-REC-001",
            tipo=TipoDocumento.PASAPORTE,
            estado=EstadoDocumento.RECIBIDO,
            fecha_expiracion=date.today() + timedelta(days=365),
            version_actual=1,
            observacion="",
        )
        _docs_of_current(context).append(doc)

    context.documento_actual = doc


@step(r"el asesor revisa el contenido del documento y es correcto")
def step_revisa_documento_correcto(context: behave.runner.Context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual.estado == EstadoDocumento.RECIBIDO, \
        "Para revisarlo como correcto, debe estar en estado RECIBIDO."
    context.error = None


@step(r'el asesor marca el documento con estado "APROBADO"')
def step_marcar_documento_aprobado(context: behave.runner.Context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual.estado == EstadoDocumento.RECIBIDO, \
        "Solo se puede aprobar un documento en estado RECIBIDO."
    context.documento_actual.estado = EstadoDocumento.APROBADO
    assert context.documento_actual.estado == EstadoDocumento.APROBADO


# --------------------- Criterio 3 ---------------------
@step(r"el asesor identifica una inconsistencia en el documento")
def step_identifica_inconsistencia(context: behave.runner.Context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual.estado == EstadoDocumento.RECIBIDO, \
        "Para identificar inconsistencia, debe estar en estado RECIBIDO."
    context.error = "Inconsistencia detectada"


@step(r"el asesor registra una observación")
def step_registra_observacion(context: behave.runner.Context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    # observación mínima
    context.documento_actual.observacion = "Inconsistencia encontrada en el documento."


@step(r'el documento queda marcado con estado "RECHAZADO"')
def step_doc_queda_rechazado(context: behave.runner.Context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    context.documento_actual.estado = EstadoDocumento.RECHAZADO
    assert context.documento_actual.estado == EstadoDocumento.RECHAZADO


# --------------------- Criterio 4 ---------------------
@step(r"que el solicitante tiene todos los documentos requeridos")
def step_tiene_todos_documentos_requeridos(context: behave.runner.Context):
    _ensure_context(context)

    # set mínimo de requeridos (ajústalo si tu proceso define otros)
    context.documentos_requeridos = [
        TipoDocumento.PASAPORTE,
        TipoDocumento.ANTECEDENTES,
    ]

    # asegurar que existan en el expediente del solicitante
    for tipo in context.documentos_requeridos:
        if _find_doc_by_tipo(context, tipo) is None:
            _docs_of_current(context).append(
                Documento(
                    id_documento=f"DOC-{tipo.value}-001",
                    tipo=tipo,
                    estado=EstadoDocumento.RECIBIDO,
                    fecha_expiracion=date.today() + timedelta(days=365),
                    version_actual=1,
                    observacion="",
                )
            )


@step(r'todos los documentos están en estado "APROBADO"')
def step_todos_documentos_aprobados(context: behave.runner.Context):
    _ensure_context(context)
    assert context.documentos_requeridos, "No se definieron documentos requeridos."

    # aprobar todos los requeridos
    for tipo in context.documentos_requeridos:
        doc = _find_doc_by_tipo(context, tipo)
        assert doc is not None, f"Falta el documento requerido: {tipo.value}"
        doc.estado = EstadoDocumento.APROBADO

    # validar condición
    for tipo in context.documentos_requeridos:
        doc = _find_doc_by_tipo(context, tipo)
        assert doc.estado == EstadoDocumento.APROBADO, f"{tipo.value} no está APROBADO."


@step(r"el asesor marca al solicitante como habilitado")
def step_marcar_solicitante_habilitado(context: behave.runner.Context):
    _ensure_context(context)
    assert context.solicitante is not None, "No existe solicitante."

    # regla: habilitado solo si los requeridos están aprobados
    for tipo in context.documentos_requeridos:
        doc = _find_doc_by_tipo(context, tipo)
        assert doc is not None, f"Falta el documento requerido: {tipo.value}"
        assert doc.estado == EstadoDocumento.APROBADO, f"El documento {tipo.value} no está APROBADO."

    context.solicitante.habilitado = True


@step(r"el solicitante queda habilitado para el proceso de visa")
def step_solicitante_queda_habilitado(context: behave.runner.Context):
    _ensure_context(context)
    assert context.solicitante is not None, "No existe solicitante."
    assert context.solicitante.habilitado is True, "El solicitante no quedó habilitado."


# --------------------- Criterio 5 ---------------------
@step(r"que existe un documento con fecha de expiración")
def step_existe_documento_con_expiracion(context: behave.runner.Context):
    _ensure_context(context)

    # documento con expiración (ayer) para forzar vencimiento
    doc = Documento(
        id_documento="DOC-EXP-001",
        tipo=TipoDocumento.PASAPORTE,
        estado=EstadoDocumento.RECIBIDO,
        fecha_expiracion=date.today() - timedelta(days=1),
        version_actual=1,
        observacion="",
    )
    _docs_of_current(context).append(doc)
    context.documento_actual = doc


@step(r'el documento se encuentra en estado "APROBADO"')
def step_documento_esta_aprobado(context: behave.runner.Context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    context.documento_actual.estado = EstadoDocumento.APROBADO
    assert context.documento_actual.estado == EstadoDocumento.APROBADO


@step(r"la fecha de hoy supera la fecha de expiración del documento")
def step_hoy_supera_expiracion(context: behave.runner.Context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual.fecha_expiracion is not None, "El documento no tiene fecha de expiración."

    hoy = date.today()
    if hoy > context.documento_actual.fecha_expiracion:
        context.documento_actual.estado = EstadoDocumento.VENCIDO
    else:
        raise AssertionError(f"Hoy ({hoy}) no supera la expiración ({context.documento_actual.fecha_expiracion}).")


@step(r'el documento queda marcado con estado "VENCIDO"')
def step_doc_queda_vencido(context: behave.runner.Context):
    _ensure_context(context)
    assert context.documento_actual is not None, "No existe documento actual."
    assert context.documento_actual.estado == EstadoDocumento.VENCIDO, \
        f"Se esperaba VENCIDO, pero fue {context.documento_actual.estado.value}"
