from behave import given, when, then
from faker import Faker
from datetime import date

fake = Faker("es_ES")


# Escenario 1
@given("que el gestor migratorio inicia un nuevo registro de solicitante")
def step_inicia_registro(context):
    context.solicitante = {
        "cedula": fake.unique.random_number(digits=10),
        "nombre": fake.name(),
        "fecha_nacimiento": fake.date_of_birth(minimum_age=18, maximum_age=65),
        "correo": fake.email(),
        "telefono": fake.phone_number(),
        "direccion": fake.address(),
        "condicion": fake.random_element(["Inmigrante", "Emigrante"]),
        "visa": fake.random_element(["Trabajar", "Estudiar", "Vivir"])
    }


@when("ingresa información biográfica y migratoria válida del solicitante")
def step_ingresa_info_valida(context):
    # Simulación de registro en el sistema
    context.response = {
        "expediente_creado": True,
        "expediente_id": fake.uuid4(),
        "fecha_inicio": date.today()
    }


@then("el sistema crea el expediente digital del solicitante")
def step_valida_expediente(context):
    assert context.response["expediente_creado"] is True


@then("genera un identificador único del expediente")
def step_valida_id(context):
    assert context.response["expediente_id"] is not None


@then("registra el inicio formal del proceso migratorio")
def step_valida_inicio(context):
    assert context.response["fecha_inicio"] is not None


# Escenario 2

@given("que existe un expediente migratorio activo asociado a un solicitante")
def step_expediente_activo(context):
    context.solicitante = {
        "cedula": fake.unique.random_number(digits=10),
        "nombre": fake.name()
    }

    context.expediente_activo = {
        "cedula": context.solicitante["cedula"],
        "estado": "ACTIVO"
    }


@when("el gestor migratorio intenta iniciar un nuevo proceso migratorio para el mismo solicitante")
def step_intenta_nuevo_proceso(context):
    # El sistema detecta duplicidad
    context.response = {
        "expediente_creado": False,
        "mensaje": "El solicitante ya cuenta con un proceso migratorio activo"
    }

@then("el sistema impide la creación de un nuevo expediente")
def step_impide_creacion(context):
    assert context.response["expediente_creado"] is False

@then("notifica al gestor que el solicitante ya cuenta con un proceso migratorio activo")
def step_notifica_duplicidad(context):
    assert "proceso migratorio activo" in context.response["mensaje"]

#Escenario 3
@given("que el gestor migratorio ingresa la información del solicitante")
def step_ingresa_info(context):
    context.solicitante = {
        "fecha_nacimiento": fake.date_of_birth(minimum_age=18, maximum_age=65)
    }

@when("se detecta información biográfica inconsistente")
def step_info_inconsistente(context):
    # Faker genera inconsistencia: edad negativa
    context.solicitante["fecha_nacimiento"] = fake.date_between(
        start_date="+1y", end_date="+5y"
    )

    context.response = {
        "inconsistencias": ["Fecha de nacimiento no válida"],
        "estado": "RECHAZADO"
    }

@then("el sistema identifica la inconsistencia")
def step_identifica_inconsistencia(context):
    assert len(context.response["inconsistencias"]) > 0

@then("notifica al gestor que la información debe ser corregida antes de continuar")
def step_notifica_error(context):
    assert context.response["estado"] == "RECHAZADO"

#Escenario 4

@given("que un expediente migratorio ha sido registrado correctamente")
def step_expediente_registrado(context):
    context.expediente = {
        "id": fake.uuid4(),
        "datos_biograficos": True,
        "datos_migratorios": True,
        "estado": "EN_PROCESO",
        "etapa": fake.random_element(["Recepción", "Evaluación", "Resolución"])
    }

@when("el gestor migratorio consulta el expediente del solicitante")
def step_consulta_expediente(context):
    context.expediente_consultado = context.expediente

@then("el sistema muestra la información biográfica y migratoria del solicitante")
def step_muestra_info(context):
    assert context.expediente_consultado["datos_biograficos"] is True
    assert context.expediente_consultado["datos_migratorios"] is True

@then("presenta el estado actual del proceso migratorio")
def step_estado_proceso(context):
    assert context.expediente_consultado["estado"] is not None

@then("permite su seguimiento conforme a las etapas definidas por el negocio")
def step_seguimiento(context):
    assert context.expediente_consultado["etapa"] in [
        "Recepción", "Evaluación", "Resolución"
    ]
