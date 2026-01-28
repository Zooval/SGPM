from __future__ import annotations

from datetime import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from SGPM.application.dtos import SolicitanteDTO
from SGPM.application.services import (
    SolicitanteService,
    DatosObligatoriosFaltantesError,
    SolicitanteDuplicadoError,
    SolicitanteNoEncontradoError,
)
from SGPM.infrastructure.repositories import DjangoSolicitanteRepository


def _require_login(request):
    if not request.session.get("asesor_email"):
        return redirect("login")
    return None


def solicitante_view(request):
    """
    Vista principal de menú de solicitantes.
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "page_title": "solicitantes",
    }
    return render(request, "solicitante/solicitante.html", context)


def registro_solicitante_view(request):
    """
    Registro de un nuevo solicitante usando SolicitanteService.
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    service = SolicitanteService(DjangoSolicitanteRepository())
    form_data = {}

    if request.method == "POST":
        try:
            cedula = (request.POST.get("cedula") or "").strip()
            nombres = (request.POST.get("nombres") or "").strip()
            apellidos = (request.POST.get("apellidos") or "").strip()
            correo = (request.POST.get("correo") or "").strip()
            telefono = (request.POST.get("telefono") or "").strip()
            fecha_nac_str = (request.POST.get("fecha_nacimiento") or request.POST.get("fechaNacimiento") or "").strip()

            form_data = {
                "cedula": cedula,
                "nombres": nombres,
                "apellidos": apellidos,
                "correo": correo,
                "telefono": telefono,
                "fecha_nacimiento": fecha_nac_str,
            }

            fecha_nacimiento = None
            if fecha_nac_str:
                fecha_nacimiento = datetime.fromisoformat(fecha_nac_str).date()

            dto = SolicitanteDTO(
                cedula=cedula,
                nombres=nombres,
                apellidos=apellidos,
                correo=correo,
                telefono=telefono,
                fecha_nacimiento=fecha_nacimiento,
                direccion="",
            )

            service.registrar_solicitante(dto)
            messages.success(request, "Solicitante registrado correctamente.")
            return redirect("solicitante")

        except DatosObligatoriosFaltantesError as e:
            messages.error(request, str(e))
        except SolicitanteDuplicadoError as e:
            messages.error(request, str(e))
        except ValueError:
            messages.error(request, "Fecha de nacimiento inválida.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error al registrar el solicitante: {e}")

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "page_title": "registro solicitantes",
        "form_data": form_data,
    }
    return render(request, "solicitante/registro_solicitante.html", context)


def actualizar_datos_view(request):
    """
    Actualiza datos de contacto (correo, teléfono, dirección) de un solicitante.
    Por ahora, la UI es principalmente estática; se podría conectar
    un formulario específico a este endpoint.
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    service = SolicitanteService(DjangoSolicitanteRepository())

    solicitante = None
    cedula_busqueda = (request.GET.get("cedula") or "").strip()

    # Búsqueda solo por cédula (GET)
    if cedula_busqueda:
        solicitante = service.obtener_por_cedula(cedula_busqueda)
        if solicitante is None:
            messages.error(request, f"No existe solicitante con cédula {cedula_busqueda}")

    # Actualización de datos de contacto (POST)
    if request.method == "POST":
        cedula = (request.POST.get("cedula") or "").strip()
        correo = (request.POST.get("correo") or "").strip()
        telefono = (request.POST.get("telefono") or "").strip()
        direccion = (request.POST.get("direccion") or "").strip()

        try:
            actualizado = service.actualizar_contacto(cedula, correo, telefono, direccion)
            messages.success(request, "Datos de contacto actualizados correctamente.")
            solicitante = actualizado
            cedula_busqueda = cedula
        except (DatosObligatoriosFaltantesError, SolicitanteNoEncontradoError) as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Ocurrió un error al actualizar los datos: {e}")

    # Para listado de solicitantes asociados (simple tabla)
    solicitantes_lista = service.listar_todos()

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "page_title": "actualizar datos",
        "solicitante": solicitante,
        "cedula_busqueda": cedula_busqueda,
        "solicitantes_lista": solicitantes_lista,
    }
    return render(request, "solicitante/actualizacion_datos.html", context)


def consulta_expedientes_view(request):
    """
    Consulta de expedientes de solicitantes.
    De momento solo renderiza la vista; la búsqueda detallada
    puede conectarse luego con SolicitudMigratoriaService.
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "page_title": "consulta expedientes",
    }
    return render(request, "solicitante/consulta_expediente.html", context)