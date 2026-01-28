from __future__ import annotations

from django.contrib import messages
from django.shortcuts import render, redirect

from SGPM.application.services import SolicitudMigratoriaService, SolicitudNoEncontradaError
from SGPM.infrastructure.repositories import (
    DjangoSolicitudMigratoriaRepository,
    DjangoSolicitanteRepository,
    DjangoAsesorRepository,
)


def _require_login(request):
    if not request.session.get("asesor_email"):
        return redirect("login")
    return None


def solicitud_view(request):
    """
    Vista de menú principal de solicitudes.
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "page_title": "solicitudes",
    }
    return render(request, "solicitudes/solicitudes.html", context)


def registro_solicitud_view(request):
    """
    Registro de una nueva solicitud migratoria usando SolicitudMigratoriaService.
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    service = SolicitudMigratoriaService(
        DjangoSolicitudMigratoriaRepository(),
        solicitante_repo=DjangoSolicitanteRepository(),
        asesor_repo=DjangoAsesorRepository(),
    )

    form_data = {}

    if request.method == "POST":
        from django.utils import timezone
        from SGPM.application.dtos import SolicitudMigratoriaDTO

        codigo = (request.POST.get("codigo") or "").strip()
        tipo_servicio = (request.POST.get("tipo_servicio") or "").strip()
        cedula = (request.POST.get("solicitante_cedula") or "").strip()

        form_data = {
            "codigo": codigo,
            "tipo_servicio": tipo_servicio,
            "solicitante_cedula": cedula,
        }

        try:
            if not codigo or not tipo_servicio:
                messages.error(request, "Código y tipo de servicio son obligatorios.")
            else:
                dto = SolicitudMigratoriaDTO(
                    codigo=codigo,
                    tipo_servicio=tipo_servicio,
                    estado_actual="CREADA",
                    fecha_creacion=timezone.now(),
                    fecha_expiracion=None,
                    solicitante_cedula=cedula or None,
                    asesor_email=request.session.get("asesor_email"),
                    fechas_proceso={},
                )
                service.crear_solicitud(dto)
                messages.success(request, "Solicitud creada correctamente.")
                return redirect("listado")
        except Exception as e:
            messages.error(request, f"Ocurrió un error al crear la solicitud: {e}")

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "page_title": "registro solicitudes",
        "form_data": form_data,
    }
    return render(request, "solicitudes/registro.html", context)


def listado_view(request):
    """
    Lista de solicitudes usando SolicitudMigratoriaService.
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    service = SolicitudMigratoriaService(
        DjangoSolicitudMigratoriaRepository(),
        solicitante_repo=DjangoSolicitanteRepository(),
        asesor_repo=DjangoAsesorRepository(),
    )
    solicitudes = service.listar_todas()

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "page_title": "listado solicitudes",
        "solicitudes": solicitudes,
    }
    return render(request, "solicitudes/listado.html", context)


def detalle_view(request):
    """
    Consulta de detalle de una solicitud.
    (por ahora, solo renderiza la vista; la lógica detallada se puede conectar
    vía endpoints adicionales o parámetros de búsqueda).
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "page_title": "detalle solicitudes",
    }
    return render(request, "solicitudes/detalle.html", context)


def cambio_estado_view(request):
    """
    Pantalla de cambio de estado.
    Aquí podríamos, en una siguiente iteración, procesar un POST que
    llame a SolicitudMigratoriaService.cambiar_estado.
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "page_title": "cambio estado",
    }
    return render(request, "solicitudes/cambio_estado.html", context)


def gestion_fechas_view(request):
    """
    Pantalla de gestión de fechas clave.
    La lógica de backend se puede conectar con asignar_fecha_proceso
    de SolicitudMigratoriaService en una fase posterior.
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "page_title": "gestion fechas",
    }
    return render(request, "solicitudes/gestion_fechas.html", context)


def documentos_menu_view(request):
    """
    Pantalla de entrada para gestionar documentos de una solicitud.
    Pide el código y redirige a la vista de documentos.
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    codigo = ""
    if request.method == "POST":
        codigo = (request.POST.get("codigo") or "").strip()
        if not codigo:
            messages.error(request, "Ingresa el código de la solicitud.")
        else:
            return redirect("solicitud_documentos", codigo=codigo)

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "page_title": "documentos solicitud",
        "codigo": codigo,
    }
    return render(request, "solicitudes/documentos_menu.html", context)