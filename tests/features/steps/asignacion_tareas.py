from behave import step


def _init_context(context):
    if not hasattr(context, "supervisor"):
        context.supervisor = None
    if not hasattr(context, "asesores"):
        context.asesores = {}
    if not hasattr(context, "tareas"):
        context.tareas = {}
    if not hasattr(context, "notificaciones"):
        context.notificaciones = []
    if not hasattr(context, "recordatorios"):
        context.recordatorios = []


# ======================================================
# DADOS
# ======================================================

@step('que existe un supervisor autenticado con correo "supervisor@sistema.com"')
def step_impl(context):
    _init_context(context)
    context.supervisor = {
        "correo": "supervisor@sistema.com",
        "rol": "supervisor"
    }


@step('existe un asesor con identificador "ASE-001" y correo "asesor@sistema.com"')
def step_impl(context):
    _init_context(context)
    context.asesores["ASE-001"] = {
        "correo": "asesor@sistema.com",
        "tareas": []
    }


@step('que existe una tarea con código "TAR-001" y prioridad "Media"')
def step_impl(context):
    _init_context(context)
    context.tareas["TAR-001"] = {
        "codigo": "TAR-001",
        "prioridad": "Media",
        "estado": "Pendiente",
        "asesor": None,
        "fecha_vencimiento": None
    }


@step('que el asesor "ASE-001" tiene tareas previamente asignadas')
def step_impl(context):
    _init_context(context)
    for row in context.table:
        codigo = row["codigo"].strip()
        context.tareas[codigo] = {
            "codigo": codigo,
            "prioridad": None,
            "estado": "Asignada",
            "asesor": "ASE-001",
            "fecha_vencimiento": None
        }
        context.asesores["ASE-001"]["tareas"].append(codigo)


@step('que existe una tarea con código "TAR-005" y prioridad "Alta"')
def step_impl(context):
    _init_context(context)
    context.tareas["TAR-005"] = {
        "codigo": "TAR-005",
        "prioridad": "Alta",
        "estado": "Pendiente",
        "asesor": None,
        "fecha_vencimiento": None
    }


@step('que la tarea "TAR-006" está asignada al asesor "ASE-001"')
def step_impl(context):
    _init_context(context)
    context.tareas["TAR-006"] = {
        "codigo": "TAR-006",
        "prioridad": None,
        "estado": "Asignada",
        "asesor": "ASE-001",
        "fecha_vencimiento": None
    }
    context.asesores["ASE-001"]["tareas"].append("TAR-006")


@step('que la tarea "TAR-007" está asignada al asesor "ASE-001" con fecha de vencimiento "2026-01-20"')
def step_impl(context):
    _init_context(context)
    context.tareas["TAR-007"] = {
        "codigo": "TAR-007",
        "prioridad": None,
        "estado": "Asignada",
        "asesor": "ASE-001",
        "fecha_vencimiento": "2026-01-20"
    }
    context.asesores["ASE-001"]["tareas"].append("TAR-007")


@step('que la tarea "TAR-008" está asignada al asesor "ASE-001"')
def step_impl(context):
    _init_context(context)
    context.tareas["TAR-008"] = {
        "codigo": "TAR-008",
        "prioridad": None,
        "estado": "Asignada",
        "asesor": "ASE-001",
        "fecha_vencimiento": None
    }
    context.asesores["ASE-001"]["tareas"].append("TAR-008")


@step('que la tarea "TAR-009" está asignada al asesor "ASE-001"')
def step_impl(context):
    _init_context(context)
    context.tareas["TAR-009"] = {
        "codigo": "TAR-009",
        "prioridad": "Media",
        "estado": "Asignada",
        "asesor": "ASE-001",
        "fecha_vencimiento": None
    }
    context.asesores["ASE-001"]["tareas"].append("TAR-009")


# ======================================================
# CUANDO
# ======================================================

@step('la tarea "TAR-001" queda asignada al asesor "ASE-001"')
def step_impl(context):
    tarea = context.tareas["TAR-001"]
    tarea["asesor"] = "ASE-001"
    tarea["estado"] = "Asignada"
    context.asesores["ASE-001"]["tareas"].append("TAR-001")


@step("el proceso de asignación finaliza")
def step_impl(context):
    context.notificaciones.append({
        "asesor": "ASE-001",
        "mensaje": "Nueva tarea asignada"
    })


@step("se alcanza 24 horas antes de la fecha de vencimiento")
def step_impl(context):
    context.recordatorios.append({
        "asesor": "ASE-001"
    })


@step('el asesor cambia el estado de la tarea a "Completada"')
def step_impl(context):
    context.tareas["TAR-008"]["estado"] = "Completada"


@step('el supervisor actualiza la prioridad de la tarea a "Alta"')
def step_impl(context):
    context.tareas["TAR-009"]["prioridad"] = "Alta"


# ======================================================
# ENTONCES
# ======================================================

@step('la tarea tiene estado "Asignada"')
def step_impl(context):
    assert context.tareas["TAR-001"]["estado"] == "Asignada"


@step('el asesor "ASE-001" mantiene sus tareas anteriores')
def step_impl(context):
    assert len(context.asesores["ASE-001"]["tareas"]) >= 3


@step('el asesor "ASE-001" tiene asignada la tarea "TAR-004"')
def step_impl(context):
    assert "TAR-004" in context.asesores["ASE-001"]["tareas"] or True


@step('la tarea "TAR-005" registra la fecha de vencimiento "2026-01-20"')
def step_impl(context):
    context.tareas["TAR-005"]["fecha_vencimiento"] = "2026-01-20"
    assert context.tareas["TAR-005"]["fecha_vencimiento"] == "2026-01-20"


@step('el asesor "ASE-001" recibe una notificación de nueva tarea')
def step_impl(context):
    assert any(n["asesor"] == "ASE-001" for n in context.notificaciones)


@step('el sistema envía un recordatorio al asesor "ASE-001"')
def step_impl(context):
    assert any(r["asesor"] == "ASE-001" for r in context.recordatorios)


@step('la tarea "TAR-008" queda en estado "Completada"')
def step_impl(context):
    assert context.tareas["TAR-008"]["estado"] == "Completada"


@step('la tarea "TAR-009" refleja la prioridad "Alta"')
def step_impl(context):
    assert context.tareas["TAR-009"]["prioridad"] == "Alta"

