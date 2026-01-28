from __future__ import annotations

from datetime import datetime, date, time
from uuid import uuid4

from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.utils import timezone

from SGPM.application.dtos import CitaDTO
from SGPM.application.services import CitaService, HorarioNoDisponibleError, CitaInvalidaError
from SGPM.domain.enums import TipoCita
from SGPM.infrastructure.models import Cita as CitaModel, SolicitudMigratoria as SolicitudModel
from SGPM.infrastructure.repositories import DjangoCitaRepository


def _require_login(request):
    if not request.session.get("asesor_email"):
        return redirect("login")
    return None


def _parse_datetime_local(value: str | None) -> datetime | None:
    if not value:
        return None
    dt = datetime.fromisoformat(value)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def _get_fecha_from_request(request) -> date:
    raw = request.GET.get("fecha")
    if not raw:
        return timezone.localdate()
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return timezone.localdate()
def listar_citas_view(request):
    """
    Lista citas en formato calendario/agenda
    - ADMIN: Ve todas las citas
    - ASESOR: Solo ve sus citas
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    fecha = _get_fecha_from_request(request)
    tz = timezone.get_current_timezone()
    inicio = timezone.make_aware(datetime.combine(fecha, time.min), tz)
    fin = timezone.make_aware(datetime.combine(fecha, time.max), tz)

    qs = CitaModel.objects.select_related(
        "solicitud",
        "solicitud__solicitante",
        "solicitud__asesor",
    ).filter(inicio__gte=inicio, inicio__lte=fin)

    rol = request.session.get("asesor_rol")
    email = request.session.get("asesor_email")
    if rol != "SUPERVISOR":
        qs = qs.filter(solicitud__asesor__email_asesor=email)

    citas = list(qs.order_by("inicio"))

    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
        'fecha': fecha,
        'citas': citas,
    }
    return render(request, 'citas/listar.html', context)


def crear_cita_view(request):
    """
    Crea una nueva cita
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    cita_service = CitaService(DjangoCitaRepository())

    if request.method == "POST":
        try:
            solicitud_codigo = (request.POST.get("solicitud_id") or "").strip()
            tipo = (request.POST.get("tipo") or "").strip()
            inicio = _parse_datetime_local(request.POST.get("inicio"))
            fin = _parse_datetime_local(request.POST.get("fin"))
            observacion = (request.POST.get("observacion") or "").strip()

            if not solicitud_codigo or not tipo or not inicio or not fin:
                messages.error(request, "Completa los campos obligatorios.")
            elif fin <= inicio:
                messages.error(request, "La fecha/hora de fin debe ser mayor que la de inicio.")
            else:
                dto = CitaDTO(
                    id_cita=str(uuid4()),
                    solicitud_codigo=solicitud_codigo,
                    tipo=tipo,
                    inicio=inicio,
                    fin=fin,
                    observacion=observacion,
                )
                cita_service.agendar_cita(dto)
                messages.success(request, "Cita creada correctamente.")
                return redirect("citas_listar")

        except HorarioNoDisponibleError as e:
            messages.error(request, str(e))
        except CitaInvalidaError as e:
            messages.error(request, str(e))
        except SolicitudModel.DoesNotExist:
            messages.error(request, "La solicitud seleccionada no existe (vuelve a seleccionarla).")
        except KeyError:
            messages.error(request, "Tipo de cita inválido.")
        except IntegrityError as e:
            messages.error(request, f"No se pudo guardar la cita: {e}")
        except Exception as e:
            messages.error(request, f"Ocurrió un error al crear la cita: {e}")

    rol = request.session.get("asesor_rol")
    email = request.session.get("asesor_email")
    solicitudes_qs = SolicitudModel.objects.select_related("solicitante", "asesor")
    if rol != "SUPERVISOR":
        solicitudes_qs = solicitudes_qs.filter(asesor__email_asesor=email)

    solicitudes = list(solicitudes_qs.order_by("-fecha_creacion")[:200])

    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
        'solicitudes': solicitudes,
        'tipos_cita': list(TipoCita),
    }
    return render(request, 'citas/crear.html', context)

def reprogramar_cita_view(request, cita_id):
    """
    Reprograma una cita
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    cita_service = CitaService(DjangoCitaRepository())

    cita = CitaModel.objects.select_related(
        "solicitud",
        "solicitud__solicitante",
        "solicitud__asesor",
    ).filter(id_cita=cita_id).first()

    if cita is None:
        messages.error(request, f"No existe la cita {cita_id}")
        return redirect("citas_listar")

    if request.method == "POST":
        try:
            nuevo_inicio = _parse_datetime_local(request.POST.get("nuevo_inicio"))
            nuevo_fin = _parse_datetime_local(request.POST.get("nuevo_fin"))
            motivo = (request.POST.get("observacion") or "").strip()

            if not nuevo_inicio or not nuevo_fin:
                messages.error(request, "Debe especificar inicio y fin.")
            else:
                cita_service.reprogramar_cita(cita_id, nuevo_inicio, nuevo_fin, motivo=motivo)
                messages.success(request, "Cita reprogramada correctamente.")
                return redirect("citas_listar")

        except HorarioNoDisponibleError as e:
            messages.error(request, str(e))
        except CitaInvalidaError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, "Ocurrió un error al reprogramar la cita.")

    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
        'cita': cita,
    }
    return render(request, 'citas/reprogramar.html', context)


def cancelar_cita_view(request, cita_id: str):
    """
    Cancela una cita (POST).
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    if request.method != "POST":
        return redirect("citas_listar")

    cita_service = CitaService(DjangoCitaRepository())
    try:
        cita_service.cancelar_cita(cita_id, motivo="")
        messages.success(request, "Cita cancelada.")
    except Exception as e:
        messages.error(request, str(e))

    return redirect("citas_listar")


def eliminar_cita_view(request, cita_id: str):
    """
    Elimina una cita (solo si está CANCELADA) (POST).
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    if request.method != "POST":
        return redirect("citas_listar")

    cita = CitaModel.objects.filter(id_cita=cita_id).first()
    if cita is None:
        messages.error(request, "La cita no existe.")
        return redirect("citas_listar")

    if cita.estado != "CANCELADA":
        messages.error(request, "Solo se pueden eliminar citas canceladas.")
        return redirect("citas_listar")

    deleted = DjangoCitaRepository().eliminar(cita_id)
    if deleted:
        messages.success(request, "Cita eliminada.")
    else:
        messages.error(request, "No se pudo eliminar la cita.")

    return redirect("citas_listar")
    
    