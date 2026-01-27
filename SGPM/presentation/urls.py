from django.urls import path
from django.contrib.auth import views as auth_views
from .views.dashboard import dashboard_view
from .views.solicitante import solicitante_view
urlpatterns = [
    path("dashboard/", dashboard_view, name="dashboard"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("solicitante/", solicitante_view, name="solicitante"),
]
