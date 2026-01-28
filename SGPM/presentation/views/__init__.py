# SGPM/presentation/views/__init__.py

# Exportamos las vistas para que funcionen con `from .views import ...`
from .login import login_view, logout_view  # noqa: F401
from .solicitante import solicitante_view  # noqa: F401
from .solicitud import solicitud_view, listado_view, detalle_view, cambio_estado_view, gestion_fechas_view, registro_solicitud_view, documentos_menu_view  # noqa: F401
from .cita import listar_citas_view, crear_cita_view, reprogramar_cita_view, cancelar_cita_view, eliminar_cita_view  # noqa: F401
from .tarea import listar_tareas_view, crear_tarea_view, editar_tarea_view, eliminar_tarea_view, reportes_tareas_view  # noqa: F401
from .documento import gestionar_documentos_view  # noqa: F401
from .dashboard import  dashboard_view