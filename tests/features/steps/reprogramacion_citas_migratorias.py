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
    # context.sistema = SistemaCitas()
    # context.sistema.agendar(id_cita, fecha_actual, tipo_tramite)


@step('que la fecha "(?P<nueva_fecha>.+)" se encuentra disponible en el calendario')
def step_impl(context: behave.runner.Context, nueva_fecha: str):
    """Verificar que la fecha esté disponible"""
    if not hasattr(context, 'calendario_disponible'):
        context.calendario_disponible = []

    fecha_dt = datetime.strptime(nueva_fecha, '%Y-%m-%d %H:%M')
    context.calendario_disponible.append(fecha_dt)

    # context.sistema = SistemaCitas()
    # context.sistema.agendar(id_cita, fecha_actual, tipo_tramite)


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

    # context.sistema.reprogramar(id_cita, nueva_fecha)


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

    # cita = context.sistema.db.get('V-101') or context.sistema.db.get('V-102')
    # assert cita['fecha'] == nueva_fecha


@step("se debe disparar un evento de notificación para el usuario e inmigrante")
def step_impl(context: behave.runner.Context):
    """Verificar que se disparó la notificación"""
    assert len(context.notificaciones) > 0, "No se generaron notificaciones"

    ultima_notificacion = context.notificaciones[-1]
    assert ultima_notificacion['tipo'] == 'reprogramacion', "Tipo de notificación incorrecto"
    assert len(ultima_notificacion['destinatarios']) >= 2, "Faltan destinatarios"

    # VERIFICACIÓN CALVE: Comprobamos que el método fue llamado sin enviar Aemail real
    # context.sistema.notification_service.send_email.assert_called()


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



@step('que existe una cita "Cita_A" programada para las "(?P<hora_original>.+)"')
def step_impl(context: behave.runner.Context, hora_original: str):

    raise NotImplementedError(u'STEP: Dado que existe una cita "Cita_A" programada para las "<hora_original>"')


@step('que existe otro evento "Evento_B" ya confirmado a las "(?P<hora_destino>.+)"')
def step_impl(context: behave.runner.Context, hora_destino: str):

    raise NotImplementedError(u'STEP: Y que existe otro evento "Evento_B" ya confirmado a las "<hora_destino>"')


@step('el asesor intenta reprogramar la "Cita_A" para las "(?P<hora_destino>.+)"')
def step_impl(context: behave.runner.Context, hora_destino: str):

    raise NotImplementedError(u'STEP: Cuando el asesor intenta reprogramar la "Cita_A" para las "<hora_destino>"')


@step('el sistema debe lanzar un error de tipo "(?P<tipo_error>.+)"')
def step_impl(context: behave.runner.Context, tipo_error: str):

    raise NotImplementedError(u'STEP: Entonces el sistema debe lanzar un error de tipo "<tipo_error>"')


@step('la "Cita_A" debe permanecer agendada a las "(?P<hora_original>.+)"')
def step_impl(context: behave.runner.Context, hora_original: str):

    raise NotImplementedError(u'STEP: Y la "Cita_A" debe permanecer agendada a las "<hora_original>"')


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

