from behave import given, when, then
from datetime import datetime
from enum import Enum
from faker import Faker
from SGPM.domain.enums import *
from SGPM.domain.entities import *

# Inicializar Faker con locale español
fake = Faker('es_ES')


# ============================================================================
# CLASES DE DOMINIO SEGÚN EL DIAGRAMA UML
# ============================================================================

class Documento:
    """Representa un documento según el diagrama"""

    def __init__(self, id_documento, tipo, estado=EstadoDocumento.RECIBIDO):
        self._id = id_documento
        self._tipo = tipo
        self._estado = estado
        self._fecha_expiracion = None
        self._version_actual = 1
        self._observacion = None

    def obtener_tipo(self):
        """Retorna el tipo del documento"""
        return self._tipo

    def obtener_id(self):
        """Retorna el ID del documento"""
        return self._id

    def marcar_como_rechazado(self, observacion):
        """Marca el documento como rechazado con una observación"""
        self._estado = EstadoDocumento.RECHAZADO
        self._observacion = observacion

    def marcar_como_aprobado(self):
        """Marca el documento como aprobado"""
        self._estado = EstadoDocumento.APROBADO

    def esta_rechazado(self):
        """Verifica si el documento está rechazado"""
        return self._estado == EstadoDocumento.RECHAZADO

    def esta_aprobado(self):
        """Verifica si el documento está aprobado"""
        return self._estado == EstadoDocumento.APROBADO

    def tiene_observacion(self):
        """Verifica si el documento tiene observación registrada"""
        return self._observacion is not None and len(self._observacion) > 0


# ============================================================================
# FUNCIONES AUXILIARES PARA GENERAR DATOS CON FAKER
# ============================================================================

def generar_cedula():
    """Genera una cédula única"""
    return fake.unique.random_number(digits=10, fix_len=True)


def generar_codigo_solicitud(cedula):
    """Genera un código único para la solicitud"""
    return f"SOL-{cedula}-{fake.year()}"


def generar_id_documento(tipo):
    """Genera un ID único para cada documento"""
    return f"DOC-{tipo.value[:3]}-{fake.unique.random_number(digits=8)}"


def generar_id_notificacion():
    """Genera un ID único para notificación"""
    return f"NOT-{fake.unique.random_number(digits=6)}"


# ============================================================================
# PASOS BDD - UN SOLO ASSERT POR STEP
# ============================================================================

# ---- ANTECEDENTES ----

@given("que existe un migrante registrado con un proceso de visa activo")
def step_existe_migrante_con_proceso_visa(context):
    """
    GIVEN: Existe un migrante registrado con un proceso de visa activo

    Regla de Negocio: El solicitante debe existir en el sistema
    """
    # Crear solicitante con datos de Faker
    cedula = generar_cedula()
    context.solicitante = Solicitante(
        cedula=str(cedula),
        nombres=fake.first_name(),
        apellidos=fake.last_name(),
        correo=fake.email(),
        telefono=fake.phone_number()
    )

    # Crear solicitud migratoria asociada
    context.solicitud = SolicitudMigratoria(
        codigo=generar_codigo_solicitud(cedula),
        migrante_cedula=str(cedula),
        asignada_a=fake.email()
    )

    # Inicializar lista de notificaciones
    context.notificaciones = []

    # UN SOLO ASSERT: Verificar que el solicitante existe
    assert context.solicitante.existe(), \
        "REGLA DE NEGOCIO: El solicitante debe estar registrado en el sistema"


# ---- CRITERIO 1: Registrar documentos correctos ----

@given("que el migrante entrega su carpeta con los documentos necesarios")
def step_migrante_entrega_carpeta_documentos(context):
    """
    GIVEN: El migrante entrega su carpeta física con los documentos necesarios

    Regla de Negocio: El migrante debe entregar documentos físicos
    """
    # Crear documentos físicos entregados
    context.documentos_entregados = [
        Documento(
            generar_id_documento(TipoDocumento.PASAPORTE),
            context.solicitud._codigo,
            TipoDocumento.PASAPORTE
        ),
        Documento(
            generar_id_documento(TipoDocumento.ANTECEDENTES),
            context.solicitud._codigo,
            TipoDocumento.ANTECEDENTES
        ),
        Documento(
            generar_id_documento(TipoDocumento.ESTADOS_BANCARIOS),
            context.solicitud._codigo,
            TipoDocumento.ESTADOS_BANCARIOS
        ),
        Documento(
            generar_id_documento(TipoDocumento.CONTRATO_TRABAJO),
            context.solicitud._codigo,
            TipoDocumento.CONTRATO_TRABAJO
        ),
    ]

    # UN SOLO ASSERT: Verificar que se entregaron documentos
    assert len(context.documentos_entregados) > 0, \
        "REGLA DE NEGOCIO: El migrante debe entregar al menos un documento"


@when("el asesor  revisa la carpeta con los documentos")
def step_asesor_revisa_carpeta_documentos(context):
    context.documentos_revisados = []

    for documento in context.documentos_entregados:
        # Simular revisión: aprobar cada documento
        documento.marcar_como_aprobado()
        context.documentos_revisados.append(documento)

    # UN SOLO ASSERT: Verificar que la revisión se completó
    assert len(context.documentos_revisados) == len(context.documentos_entregados)


@then("registra los documentos")
def step_asesor_registra_documentos(context):
    """
    THEN: El asesor registra los documentos en la solicitud

    Regla de Negocio: Todos los documentos deben quedar registrados
    """
    # Registrar cada documento en la solicitud
    for documento in context.documentos_revisados:
        context.solicitud.agregar_documento(documento)

    # UN SOLO ASSERT: Verificar que los documentos fueron registrados
    assert context.solicitud.documentos_fueron_registrados(len(context.documentos_entregados))


@then("se habilita el perfil del migrante para el proceso de visa")
def step_se_habilita_perfil_migrante(context):
    # Cambiar estado de la solicitud
    if context.solicitud.esta_completa():
        context.solicitud.cambiar_estado(EstadoSolicitud.EN_REVISION)

    # UN SOLO ASSERT: Verificar que la solicitud está en revisión
    assert context.solicitud.esta_en_revision()


# ---- CRITERIO 2: Documentos con inconsistencias ----

@when("el asesor verifica la correctitud de los documentos")
def step_asesor_verifica_correctitud_documentos(context):
    """
    WHEN: El asesor verifica la correctitud de los documentos

    Regla de Negocio: Debe iniciarse un proceso de verificación
    """
    context.verificacion_iniciada = True
    context.documentos_rechazados = []

    # UN SOLO ASSERT: Verificar que la verificación inició
    assert context.verificacion_iniciada


@when("encuentra inconsistencias en los documentos")
def step_encuentra_inconsistencias(context):
    # Crear documentos con inconsistencias
    documento_rechazado = Documento(
        generar_id_documento(TipoDocumento.PASAPORTE),
        context.solicitud._codigo,
        TipoDocumento.PASAPORTE,
        EstadoDocumento.RECHAZADO
    )
    context.documentos_rechazados.append(documento_rechazado)
    context.solicitud.agregar_documento(documento_rechazado)

    # UN SOLO ASSERT: Verificar que hay documentos rechazados
    assert len(context.documentos_rechazados) > 0


@then("el asesor registra las observaciones")
def step_asesor_registra_observaciones(context):
    observaciones_posibles = [

        "Documento vencido - Debe presentar documento vigente"
    ]

    # Registrar observación en cada documento rechazado
    for documento in context.documentos_rechazados:
        observacion = fake.random_element(elements=observaciones_posibles)
        documento.marcar_como_rechazado(observacion)

    # UN SOLO ASSERT: Verificar que el primer documento tiene observación
    assert context.documentos_rechazados[0].tiene_observacion()


@then("se notifica al migrante los cambios a realizar")
def step_notifica_migrante_cambios(context):
    notificacion = Notificacion(
        id_notificacion=generar_id_notificacion(),
        destinatario=context.solicitante.obtener_correo(),
        tipo=TipoNotificacion.DOC_FALTANTE,
        mensaje=f"Se encontraron observaciones en sus documentos. Por favor revise y corrija."
    )
    context.notificaciones.append(notificacion)

    # UN SOLO ASSERT: Verificar que la notificación fue creada
    assert context.notificaciones[-1].fue_creada()


# ---- CRITERIO 3: Documentos faltantes ----

@given("que el migrante no ha entregado todos los documentos requeridos")
def step_migrante_no_entrega_todos_documentos(context):
    # Crear solo algunos documentos (incompleto)
    documentos_incompletos = [
        Documento(
            generar_id_documento(TipoDocumento.PASAPORTE),
            context.solicitud._codigo,
            TipoDocumento.PASAPORTE
        ),
        Documento(
            generar_id_documento(TipoDocumento.ANTECEDENTES),
            context.solicitud._codigo,
            TipoDocumento.ANTECEDENTES
        ),
        # FALTAN: ESTADOS_BANCARIOS y CONTRATO_TRABAJO
    ]

    for doc in documentos_incompletos:
        doc.marcar_como_aprobado()
        context.solicitud.agregar_documento(doc)

    # UN SOLO ASSERT: Verificar que hay documentos faltantes
    assert context.solicitud.tiene_documentos_faltantes()


@when("se valida la completitud de los documentos")
def step_valida_completitud_documentos(context):
    context.validacion_completa = context.solicitud.esta_completa()

    # UN SOLO ASSERT: Verificar que la solicitud NO está completa
    assert not context.validacion_completa


@then("el expediente queda marcado como incompleto")
def step_expediente_marcado_incompleto(context):
    context.solicitud.cambiar_estado(EstadoSolicitud.DOCUMENTOS_PENDIENTES)

    # UN SOLO ASSERT: Verificar el estado de la solicitud
    assert context.solicitud.tiene_documentos_pendientes()
