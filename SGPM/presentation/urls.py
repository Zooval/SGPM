from django.urls import path
from .views import *
from .views.solicitante import *
from .views.solicitud import *
from .views.dashboard import dashboard_view
from .views.documento import gestionar_documentos_view, editar_documento_view, eliminar_documento_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),


    path("solicitante/", solicitante_view, name="solicitante"),
    path("registro/", registro_solicitante_view, name="registro"),

    path("actualizar/", actualizar_datos_view, name="actualizar"),
    path("consultar/", consulta_expedientes_view, name="consultar-expediente"),

    path ("solicitud", solicitud_view, name="solicitud"),
    path("solicitud/registro/", registro_solicitud_view, name="solicitud_registro"),
    path("solicitud/listado/", listado_view, name="listado"),
    path("solicitud/detalle", detalle_view, name="detalle"),
    path("solicitud/estado/", cambio_estado_view, name="cambio-estado"),
    path("solicitud/gestion-fechas/", gestion_fechas_view, name="gestion-fechas"),
    path("solicitud/documentos/", documentos_menu_view, name="solicitud_documentos_menu"),
    path("solicitud/<str:codigo>/documentos/", gestionar_documentos_view, name="solicitud_documentos"),
    path("solicitud/documentos/<str:id_documento>/editar/", editar_documento_view, name="documento_editar"),
    path("solicitud/documentos/<str:id_documento>/eliminar/", eliminar_documento_view, name="documento_eliminar"),


    path("", login_view, name="home"),  # Redirigir raíz a login
    path("citas/", listar_citas_view, name="citas_listar"),
    path("citas/crear/", crear_cita_view, name="citas_crear"),
    path("citas/reprogramar/<str:cita_id>/", reprogramar_cita_view, name="citas_reprogramar"),
    path("citas/cancelar/<str:cita_id>/", cancelar_cita_view, name="citas_cancelar"),
    path("citas/eliminar/<str:cita_id>/", eliminar_cita_view, name="citas_eliminar"),
    path("tareas/", listar_tareas_view, name="tareas_listar"),
    path("tareas/crear/", crear_tarea_view, name="tareas_crear"),
    path("tareas/editar/<str:tarea_id>/", editar_tarea_view, name="tareas_editar"),
    path("tareas/eliminar/<str:tarea_id>/", eliminar_tarea_view, name="tareas_eliminar"),
    path("tareas/reportes/", reportes_tareas_view, name="tareas_reportes"),
]
