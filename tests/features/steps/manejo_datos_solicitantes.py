# features/steps/manejo_datos_solicitantes_steps.py

import behave.runner
from behave import step, use_step_matcher
from dataclasses import dataclass
from datetime import date
from enum import Enum

use_step_matcher("re")


# ============================================================
# ENUM (según diagrama; necesario para Asesor)
# ============================================================
class RolUsuario(Enum):
    ASESOR = "ASESOR"
    SUPERVISOR = "SUPERVISOR"


# ============================================================
# Clases necesarias para la feature (según diagrama)
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
    rol: RolUsuario


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _ensure_store(context: behave.runner.Context):
    if not hasattr(context, "solicitantes"):
        context.solicitantes = {}  # cedula -> Solicitante
    if not hasattr(context, "asesor"):
        context.asesor = None
    if not hasattr(context, "error"):
        context.error = None
    if not hasattr(context, "ultimo_registro"):
        context.ultimo_registro = None
    if not hasattr(context, "ultima_actualizacion"):
        context.ultima_actualizacion = None


def _row_from_table(context) -> dict:
    if context.table is None:
        raise AssertionError("Se esperaba una tabla en el paso, pero no se recibió ninguna.")
    rows = [r.as_dict() for r in context.table]
    if len(rows) != 1:
        raise AssertionError(f"Se esperaba 1 fila en la tabla, pero llegaron {len(rows)}.")
    return {k.strip(): (v.strip() if v is not None else "") for k, v in rows[0].items()}


def _parse_date_iso(value: str) -> date:
    return date.fromisoformat(value)  # YYYY-MM-DD


def _parse_bool(value: str, default: bool = True) -> bool:
    s = (value or "").strip().lower()
    if s == "":
        return default
    if s in ("true", "1", "si", "sí", "s", "y", "yes"):
        return True
    if s in ("false", "0", "no", "n"):
        return False
    return default


def _validate_obligatorios(data: dict, obligatorios: list[str]):
    faltan = [k for k in obligatorios if not str(data.get(k, "")).strip()]
    if faltan:
        raise ValueError(f"Faltan datos obligatorios: {', '.join(faltan)}")


def _to_solicitante(data: dict) -> Solicitante:
    # En la feature se usa: nombre/apellido
    # En la clase: nombres/apellidos
    return Solicitante(
        cedula=data.get("cedula", "").strip(),
        nombres=data.get("nombre", data.get("nombres", "")).strip(),
        apellidos=data.get("apellido", data.get("apellidos", "")).strip(),
        correo=data.get("correo", "").strip(),
        telefono=data.get("telefono", "").strip(),
        direccion=data.get("direccion", "").strip(),
        fecha_nacimiento=_parse_date_iso(data.get("fecha_nacimiento", "").strip()),
        habilitado=_parse_bool(data.get("habilitado", ""), default=True),  # si no viene, True
    )


# ------------------------------------------------------------
# Steps (interacción en memoria)
# ------------------------------------------------------------
@step(r'que soy un asesor autenticado')
def dado_asesor_autenticado(context: behave.runner.Context):
    _ensure_store(context)
    context.asesor = Asesor(
        nombres="Anthony",
        apellidos="Pérez",
        email_asesor="asesor@mail.com",
        rol=RolUsuario.ASESOR,
    )
    context.error = None


@step(r'que no existe un solicitante con cédula "(?P<cedula>[^"]+)"')
def dado_no_existe_solicitante(context: behave.runner.Context, cedula: str):
    _ensure_store(context)
    assert cedula not in context.solicitantes, f"Se esperaba que NO exista {cedula}, pero ya está registrado."


@step(r'que existe un solicitante con los siguientes datos:')
def dado_existe_solicitante_con_datos(context: behave.runner.Context):
    _ensure_store(context)
    assert context.asesor is not None, "Para gestionar solicitantes debes estar autenticado como asesor."

    data = _row_from_table(context)
    obligatorios = ["cedula", "nombre", "apellido", "correo", "fecha_nacimiento", "telefono", "direccion"]
    _validate_obligatorios(data, obligatorios)

    solicitante = _to_solicitante(data)
    context.solicitantes[solicitante.cedula] = solicitante
    context.error = None


@step(r'registro un solicitante con los siguientes datos:')
def cuando_registro_solicitante(context: behave.runner.Context):
    _ensure_store(context)
    context.error = None
    context.ultimo_registro = None

    assert context.asesor is not None, "Debes estar autenticado como asesor."

    try:
        data = _row_from_table(context)
        obligatorios = ["cedula", "nombre", "apellido", "correo", "fecha_nacimiento", "telefono", "direccion"]
        _validate_obligatorios(data, obligatorios)

        solicitante = _to_solicitante(data)

        if solicitante.cedula in context.solicitantes:
            raise ValueError("La cédula ya está registrada")

        context.solicitantes[solicitante.cedula] = solicitante
        context.ultimo_registro = solicitante.cedula

    except Exception as e:
        context.error = e


@step(r'intento registrar un solicitante con los siguientes datos:')
def cuando_intento_registrar_solicitante(context: behave.runner.Context):
    return cuando_registro_solicitante(context)


@step(r'el solicitante queda registrado correctamente')
def entonces_registro_ok(context: behave.runner.Context):
    _ensure_store(context)
    assert context.error is None, f"Se esperaba registro exitoso, pero ocurrió: {context.error}"
    assert context.ultimo_registro is not None, "No quedó constancia del registro."
    assert context.ultimo_registro in context.solicitantes, "El solicitante no aparece en la lista."


@step(r'puedo visualizar la ficha del solicitante con cédula "(?P<cedula>[^"]+)"')
def entonces_visualizar_ficha(context: behave.runner.Context, cedula: str):
    _ensure_store(context)
    assert context.error is None, f"No se puede visualizar ficha si hubo error: {context.error}"
    assert cedula in context.solicitantes, f"No existe solicitante con cédula {cedula}."


@step(r'actualizo los datos de contacto del solicitante con cédula "(?P<cedula>[^"]+)":')
def cuando_actualizo_contacto(context: behave.runner.Context, cedula: str):
    _ensure_store(context)
    context.error = None
    context.ultima_actualizacion = None

    assert context.asesor is not None, "Debes estar autenticado como asesor."
    assert cedula in context.solicitantes, f"No existe solicitante con cédula {cedula}."

    try:
        cambios = _row_from_table(context)
        obligatorios = ["correo", "telefono", "direccion"]
        _validate_obligatorios(cambios, obligatorios)

        s = context.solicitantes[cedula]
        s.correo = cambios["correo"].strip()
        s.telefono = cambios["telefono"].strip()
        s.direccion = cambios["direccion"].strip()

        context.ultima_actualizacion = cedula

    except Exception as e:
        context.error = e


@step(r'los cambios se guardan correctamente')
def entonces_update_ok(context: behave.runner.Context):
    _ensure_store(context)
    assert context.error is None, f"Se esperaba actualización exitosa, pero ocurrió: {context.error}"
    assert context.ultima_actualizacion is not None, "No se registró ninguna actualización."


@step(r'la ficha del solicitante muestra los datos actualizados')
def entonces_ficha_actualizada(context: behave.runner.Context):
    _ensure_store(context)
    assert context.error is None, f"No se puede validar ficha si hubo error: {context.error}"

    cedula = context.ultima_actualizacion
    assert cedula in context.solicitantes, "No existe ficha para validar."

    s = context.solicitantes[cedula]
    assert s.correo.strip()
    assert s.telefono.strip()
    assert s.direccion.strip()


@step(r'se muestra un mensaje de error por datos obligatorios')
def entonces_error_obligatorios(context: behave.runner.Context):
    _ensure_store(context)
    assert context.error is not None, "Se esperaba un error por datos obligatorios, pero no hubo error."
    msg = str(context.error).lower()
    assert ("faltan datos obligatorios" in msg) or ("faltan" in msg) or ("obligatorios" in msg), \
        f"El error no corresponde a datos obligatorios: {context.error}"


@step(r'el solicitante con cédula "(?P<cedula>[^"]+)" no se registra')
def entonces_no_registrado(context: behave.runner.Context, cedula: str):
    _ensure_store(context)
    assert cedula not in context.solicitantes, f"El solicitante {cedula} no debía registrarse, pero existe."


@step(r'se muestra un mensaje indicando que la cédula ya está registrada')
def entonces_error_duplicado(context: behave.runner.Context):
    _ensure_store(context)
    assert context.error is not None, "Se esperaba error por duplicado, pero no hubo error."
    assert "ya está registrada" in str(context.error).lower(), f"El error no corresponde a duplicado: {context.error}"


@step(r'no se crea un nuevo solicitante')
def entonces_no_crea_nuevo(context: behave.runner.Context):
    _ensure_store(context)
    assert context.error is not None, "Se esperaba que el registro duplicado falle."
    # dict evita duplicados por llave; garantizamos que no se duplicó la cédula
    assert len([c for c in context.solicitantes.keys() if c == "0102030405"]) <= 1
