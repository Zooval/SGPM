from datetime import datetime

import behave.runner
from behave import *
from unittest.mock import Mock
from faker import Faker

use_step_matcher("re")
fake = Faker('es_ES')

# --- Simulación del Sistema (Contexto) ---
# En un proyecto real, esto serían llamadas a tu API o Controlador
class SistemaCitas:
    def __init__(self):
        self.db = {}
        self.notification_service = Mock() # Simulamos el servicio de emails

    def agendar(self, id, fecha, tipo):
        self.db[id] = {'fecha': fecha, 'tipo': tipo}

    def reprogramar(self, id, nueva_fecha):
        if id in self.db:
            self.db[id]['fecha'] = nueva_fecha
            # Simulamos el envío
            self.notification_service.send_email(id, "Cita reprogramada")

# Definir excepciones personalizadas
class SlotNotAvailable(Exception):
    """Error cuando el horario no está disponible"""
    pass


class OverlapConflict(Exception):
    """Error cuando hay conflicto de superposición"""
    pass

@step('que existe una cita de visa con ID "(?P<id_cita>.+)" agendada para "(?P<fecha_actual>.+) de tipo "(?P<tipo_tramite>.+)"')
def step_impl(context: behave.runner.Context, id_cita: str, fecha_actual: str, tipo_tramite: str):
    """Crear una cita inicial en el sistema"""
    if not hasattr(context, 'citas'):
        context.citas = {}

    if not hasattr(context, 'notificaciones'):
        context.notificaciones = []

    # Crear cita con datos faker
    context.citas[id_cita] = {
        'id': id_cita,
        'fecha': datetime.strptime(fecha_actual, '%Y-%m-%d %H:%M'),
        'tipo_tramite': tipo_tramite,
        'migrante': {
            'nombre': fake.name(),
            'email': fake.email(),
            'telefono': fake.phone_number()
        },
        'asesor': {
            'nombre': fake.name(),
            'email': fake.email()
        },
        'estado': 'programada'
    }


@step('que la fecha "(?P<nueva_fecha>.+)" se encuentra disponible en el calendario')
def step_impl(context: behave.runner.Context, nueva_fecha: str):
    """Verificar que la fecha esté disponible"""
    if not hasattr(context, 'calendario_disponible'):
        context.calendario_disponible = []

    fecha_dt = datetime.strptime(nueva_fecha, '%Y-%m-%d %H:%M')
    context.calendario_disponible.append(fecha_dt)


@step('el asesor reprograma la cita "(?P<id_cita>.+)" para la "(?P<nueva_fecha>.+)"')
def step_impl(context: behave.runner.Context, id_cita: str, nueva_fecha: str):
    """Ejecutar la reprogramación de la cita"""
    if id_cita not in context.citas:
        raise ValueError(f"Cita {id_cita} no existe")

    nueva_fecha_dt = datetime.strptime(nueva_fecha, '%Y-%m-%d %H:%M')

    if nueva_fecha_dt not in context.calendario_disponible:
        raise ValueError(f"Fecha {nueva_fecha} no disponible")

    # Guardar fecha anterior para auditoría
    context.fecha_anterior = context.citas[id_cita]['fecha']

    # Actualizar la cita
    context.citas[id_cita]['fecha'] = nueva_fecha_dt
    context.citas[id_cita]['estado'] = 'reprogramada'

    # Disparar notificación
    context.notificaciones.append({
        'tipo': 'reprogramacion',
        'cita_id': id_cita,
        'destinatarios': [
            context.citas[id_cita]['migrante']['email'],
            context.citas[id_cita]['asesor']['email']
        ],
        'mensaje': f"Cita reprogramada para {nueva_fecha}"
    })


@step('el sistema debe registrar la nueva fecha "(?P<nueva_fecha>.+)" en la base de datos')
def step_impl(context: behave.runner.Context, nueva_fecha: str):
    """Verificar que la fecha fue actualizada correctamente"""
    nueva_fecha_dt = datetime.strptime(nueva_fecha, '%Y-%m-%d %H:%M')

    # Buscar la cita que fue reprogramada
    cita_actualizada = None
    for cita in context.citas.values():
        if cita['fecha'] == nueva_fecha_dt:
            cita_actualizada = cita
            break

    assert cita_actualizada is not None, "No se encontró cita con la nueva fecha"
    assert cita_actualizada['estado'] == 'reprogramada', "Estado de cita incorrecto"


@step("se debe disparar un evento de notificación para el usuario e inmigrante")
def step_impl(context: behave.runner.Context):
    """Verificar que se disparó la notificación"""
    assert len(context.notificaciones) > 0, "No se generaron notificaciones"

    ultima_notificacion = context.notificaciones[-1]
    assert ultima_notificacion['tipo'] == 'reprogramacion', "Tipo de notificación incorrecto"
    assert len(ultima_notificacion['destinatarios']) >= 2, "Faltan destinatarios"


@step('la cita debe conservar su categoría de trámite "(?P<tipo_tramite>.+)"')
def step_impl(context: behave.runner.Context, tipo_tramite: str):
    """Verificar que el tipo de trámite no cambió"""
    # Buscar la cita reprogramada
    cita_reprogramada = None
    for cita in context.citas.values():
        if cita['estado'] == 'reprogramada':
            cita_reprogramada = cita
            break

    assert cita_reprogramada is not None, "No se encontró cita reprogramada"
    assert cita_reprogramada['tipo_tramite'] == tipo_tramite, \
        f"Tipo de trámite cambió. Esperado: {tipo_tramite}, Actual: {cita_reprogramada['tipo_tramite']}"


"""-------------------------------------------------------------------------------------"""
@step('que existe una cita "(?P<nombre_cita>.+)" programada para las "(?P<hora_original>.+)"')
def step_impl(context: behave.runner.Context, nombre_cita: str, hora_original: str):
    """Crear una cita identificada por nombre"""
    if not hasattr(context, 'citas_nombradas'):
        context.citas_nombradas = {}

    if not hasattr(context, 'eventos'):
        context.eventos = {}

    fecha_dt = datetime.strptime(hora_original, '%Y-%m-%d %H:%M')

    context.citas_nombradas[nombre_cita] = {
        'id': fake.uuid4()[:8],
        'nombre': nombre_cita,
        'fecha': fecha_dt,
        'tipo_tramite': fake.random_element(['Visa_Turismo', 'Visa_Trabajo', 'Visa_Estudiante']),
        'migrante': {
            'nombre': fake.name(),
            'email': fake.email()
        },
        'asesor': {
            'nombre': fake.name(),
            'id': fake.uuid4()[:8]
        },
        'estado': 'programada'
    }


@step('que existe otro evento "(?P<nombre_evento>.+)" ya confirmado a las "(?P<hora_destino>.+)"')
def step_impl(context: behave.runner.Context, nombre_evento: str, hora_destino: str):
    """Crear un evento que bloquea el horario destino"""
    if not hasattr(context, 'eventos'):
        context.eventos = {}

    fecha_dt = datetime.strptime(hora_destino, '%Y-%m-%d %H:%M')

    context.eventos[nombre_evento] = {
        'id': fake.uuid4()[:8],
        'nombre': nombre_evento,
        'fecha': fecha_dt,
        'tipo': fake.random_element(['reunion', 'capacitacion', 'cita_otro_migrante']),
        'estado': 'confirmado',
        'asesor_id': context.citas_nombradas.get('Cita_A', {}).get('asesor', {}).get('id')
    }


@step('el asesor intenta reprogramar la "(?P<nombre_cita>.+)" para las "(?P<hora_destino>.+)"')
def step_impl(context: behave.runner.Context, nombre_cita: str, hora_destino: str):
    """Intentar reprogramar y capturar el error"""
    if nombre_cita not in context.citas_nombradas:
        raise ValueError(f"Cita {nombre_cita} no existe")

    nueva_fecha_dt = datetime.strptime(hora_destino, '%Y-%m-%d %H:%M')

    # Verificar conflictos
    tiene_conflicto = False
    tipo_conflicto = None

    for evento in context.eventos.values():
        if evento['fecha'] == nueva_fecha_dt and evento['estado'] == 'confirmado':
            tiene_conflicto = True
            # Determinar tipo de conflicto
            if evento['tipo'] == 'cita_otro_migrante':
                tipo_conflicto = 'SlotNotAvailable'
            else:
                tipo_conflicto = 'OverlapConflict'
            break

    # Guardar información del intento
    context.intento_reprogramacion = {
        'cita': nombre_cita,
        'nueva_fecha': nueva_fecha_dt,
        'tiene_conflicto': tiene_conflicto,
        'tipo_error': tipo_conflicto
    }

    # Lanzar excepción si hay conflicto
    if tiene_conflicto:
        if tipo_conflicto == 'SlotNotAvailable':
            context.error_capturado = SlotNotAvailable(
                f"El horario {hora_destino} no está disponible"
            )
        elif tipo_conflicto == 'OverlapConflict':
            context.error_capturado = OverlapConflict(
                f"Conflicto de superposición en {hora_destino}"
            )
    else:
        context.error_capturado = None


@step('el sistema debe lanzar un error de tipo "(?P<tipo_error>.+)"')
def step_impl(context: behave.runner.Context, tipo_error: str):
    """Verificar que se lanzó el error correcto"""
    assert hasattr(context, 'error_capturado'), "No se capturó ningún error"
    assert context.error_capturado is not None, "No se generó error"

    # Mapeo de nombres de error a clases
    errores_esperados = {
        'SlotNotAvailable': SlotNotAvailable,
        'OverlapConflict': OverlapConflict
    }

    clase_esperada = errores_esperados.get(tipo_error)
    assert clase_esperada is not None, f"Tipo de error desconocido: {tipo_error}"

    assert isinstance(context.error_capturado, clase_esperada), \
        f"Error incorrecto. Esperado: {tipo_error}, Obtenido: {type(context.error_capturado).__name__}"


@step('la "(?P<nombre_cita>.+)" debe permanecer agendada a las "(?P<hora_original>.+)"')
def step_impl(context: behave.runner.Context, nombre_cita: str, hora_original: str):
    """Verificar que la cita no fue modificada"""
    assert nombre_cita in context.citas_nombradas, f"Cita {nombre_cita} no existe"

    cita = context.citas_nombradas[nombre_cita]
    fecha_original_dt = datetime.strptime(hora_original, '%Y-%m-%d %H:%M')

    assert cita['fecha'] == fecha_original_dt, \
        f"La fecha de la cita cambió. Original: {hora_original}, Actual: {cita['fecha']}"

    assert cita['estado'] == 'programada', \
        f"El estado de la cita cambió. Esperado: 'programada', Actual: {cita['estado']}"


"""-------------------------------------------------------------------------------------"""
@step('que el usuario activo tiene el rol de "(?P<rol_asignado>.+)"')
def step_impl(context: behave.runner.Context, rol_asignado: str):

    raise NotImplementedError(u'STEP: Dado que el usuario activo tiene el rol de "<rol_asignado>"')


@step('existe una cita activa con ID "(?P<id_cita>.+)"')
def step_impl(context: behave.runner.Context, id_cita: str):

    raise NotImplementedError(u'STEP: Y existe una cita activa con ID "<id_cita>"')


@step('el usuario intenta ejecutar la acción de "Reprogramar" sobre la cita "(?P<id_cita>.+)"')
def step_impl(context: behave.runner.Context, id_cita: str):

    raise NotImplementedError(
        u'STEP: Cuando el usuario intenta ejecutar la acción de "Reprogramar" sobre la cita "<id_cita>"')


@step("el sistema debe rechazar la solicitud")
def step_impl(context: behave.runner.Context):
 
    raise NotImplementedError(u'STEP: Entonces el sistema debe rechazar la solicitud')


@step('se debe mostrar el mensaje de error: "(?P<mensaje_esperado>.+)"')
def step_impl(context: behave.runner.Context, mensaje_esperado: str):

    raise NotImplementedError(u'STEP: Y se debe mostrar el mensaje de error: "<mensaje_esperado>"')


@step('el sistema debe escribir una entrada en el Log de Auditoría con el código "(?P<codigo_evento>.+)"')
def step_impl(context: behave.runner.Context, codigo_evento: str):

    raise NotImplementedError(
        u'STEP: Y el sistema debe escribir una entrada en el Log de Auditoría con el código "<codigo_evento>"')

