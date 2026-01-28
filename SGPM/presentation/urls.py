from django.urls import path
from django.contrib.auth import views as auth_views
from .views.login import login_view, logout_view
from .views.dashboard import dashboard_view
from .views.solicitante import solicitante_view, registro_solicitante_view, actualizar_datos_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("solicitante/", solicitante_view, name="solicitante"),
    path("registro/", registro_solicitante_view, name="registro"),

    path("actualizar/", actualizar_datos_view, name="actualizar"),
    path("", login_view, name="home"),  # Redirigir raíz a login
]
