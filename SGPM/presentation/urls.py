from django.urls import path
from django.contrib.auth import views as auth_views
from .views.login import login_view, logout_view
from .views.dashboard import dashboard_view
from .views.solicitante import *
from .views.solicitud import *

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("solicitante/", solicitante_view, name="solicitante"),
    path("registro/", registro_solicitante_view, name="registro"),

    path("actualizar/", actualizar_datos_view, name="actualizar"),
    path("consultar/", consulta_expedientes_view, name="consultar-expediente"),

    path ("solicitud", solicitud_view, name="solicitud"),
    path("solicitud/listado/", listado_view, name="listado"),
    path("solicitud/detalle", detalle_view, name="detalle"),
    path("solicitud/estado/", cambio_estado_view, name="cambio-estado"),
    path("", login_view, name="home"),  # Redirigir raíz a login
]
