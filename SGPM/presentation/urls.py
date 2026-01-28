from django.urls import path
from .views import (
    login_view, logout_view, dashboard_view, solicitante_view,
    listar_citas_view, crear_cita_view, reprogramar_cita_view,
    listar_tareas_view, crear_tarea_view, editar_tarea_view, eliminar_tarea_view, reportes_tareas_view
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("", login_view, name="home"),  # Redirigir raíz a login
    path("solicitante/", solicitante_view, name="solicitante"),
    path("citas/", listar_citas_view, name="citas_listar"),
    path("citas/crear/", crear_cita_view, name="citas_crear"),
    path("citas/reprogramar/<str:cita_id>/", reprogramar_cita_view, name="citas_reprogramar"),
    path("tareas/", listar_tareas_view, name="tareas_listar"),
    path("tareas/crear/", crear_tarea_view, name="tareas_crear"),
    path("tareas/editar/<str:tarea_id>/", editar_tarea_view, name="tareas_editar"),
    path("tareas/eliminar/<str:tarea_id>/", eliminar_tarea_view, name="tareas_eliminar"),
    path("tareas/reportes/", reportes_tareas_view, name="tareas_reportes"),
]
