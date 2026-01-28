from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from SGPM.application.dtos import TareaDTO
from SGPM.application.services import (
    AsesorService,
    ReporteTareasService,
    TareaService,
    TareaNoEncontradaError,
    AsesorNoEncontradoError,
    ServiceError,
)
from SGPM.domain.enums import EstadoTarea, PrioridadTarea
from SGPM.infrastructure.repositories import DjangoTareaRepository, DjangoAsesorRepository


def _require_login(request):
    if not request.session.get("asesor_email"):
        return redirect("login")
    return None


def _parse_datetime_local(value: str | None) -> datetime | None:
    if not value:
        return None
    # input type="datetime-local" -> "YYYY-MM-DDTHH:MM" (sin zona)
    dt = datetime.fromisoformat(value)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt

def listar_tareas_view(request):
    """
    Lista todas las tareas
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    tarea_service = TareaService(DjangoTareaRepository(), asesor_repo=DjangoAsesorRepository())

    # Supervisor ve todo; asesor solo sus tareas
    rol = request.session.get("asesor_rol")
    email = request.session.get("asesor_email")
    tareas = tarea_service.listar_todas() if rol == "SUPERVISOR" else tarea_service.listar_por_asesor(email)

    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
        'tareas': tareas,
    }
    return render(request, 'tareas/listar.html', context)
    
def crear_tarea_view(request):
    """
    Crea una nueva tarea
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    tarea_service = TareaService(DjangoTareaRepository(), asesor_repo=DjangoAsesorRepository())

    if request.method == "POST":
        try:
            titulo = (request.POST.get("titulo") or "").strip()
            prioridad = (request.POST.get("prioridad") or "").strip()
            estado = (request.POST.get("estado") or "PENDIENTE").strip()
            comentario = (request.POST.get("comentario") or "").strip()
            vencimiento = _parse_datetime_local(request.POST.get("vencimiento"))
            asesor_email = (request.POST.get("asesor_email") or "").strip() or None

            if not titulo or not prioridad:
                messages.error(request, "Título y prioridad son obligatorios.")
            else:
                dto = TareaDTO(
                    id_tarea=str(uuid4()),
                    titulo=titulo,
                    prioridad=prioridad,
                    estado=estado,
                    vencimiento=vencimiento,
                    comentario=comentario,
                )
                creada = tarea_service.crear_tarea(dto)

                if asesor_email:
                    tarea_service.asignar_a_asesor(creada.id_tarea, asesor_email, vencimiento=vencimiento)

                messages.success(request, "Tarea creada correctamente.")
                return redirect("tareas_listar")

        except (AsesorNoEncontradoError, TareaNoEncontradaError) as e:
            messages.error(request, str(e))
        except ServiceError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, "Ocurrió un error al crear la tarea.")

    # Solo asesores con rol ASESOR para asignación de tareas
    asesores_activos = AsesorService(DjangoAsesorRepository()).listar_activos()
    asesores = [a for a in asesores_activos if a.rol == "ASESOR"]
    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
        'estados': list(EstadoTarea),
        'prioridades': list(PrioridadTarea),
        'asesores': asesores,
    }
    return render(request, 'tareas/crear.html', context)
    
    
def editar_tarea_view(request, tarea_id):
    """
    Edita una tarea
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    tarea_service = TareaService(DjangoTareaRepository(), asesor_repo=DjangoAsesorRepository())

    tarea = tarea_service.obtener_por_id(tarea_id)
    if tarea is None:
        messages.error(request, f"No existe la tarea {tarea_id}")
        return redirect("tareas_listar")

    if request.method == "POST":
        try:
            rol = request.session.get("asesor_rol")

            # Supervisor puede editar todo; asesor solo estado/comentario (si lo deseas, aquí lo mantenemos simple)
            titulo = (request.POST.get("titulo") or "").strip() if rol == "SUPERVISOR" else None
            prioridad = (request.POST.get("prioridad") or "").strip() if rol == "SUPERVISOR" else None
            vencimiento = _parse_datetime_local(request.POST.get("vencimiento")) if rol == "SUPERVISOR" else None
            comentario = (request.POST.get("comentario") or "").strip()

            estado = (request.POST.get("estado") or "").strip() or None

            asesor_email = (request.POST.get("asesor_email") or "").strip() or None

            tarea_service.editar_tarea(
                tarea_id,
                titulo=titulo,
                prioridad=prioridad or None,
                estado=estado,
                vencimiento=vencimiento,
                comentario=comentario,
            )

            if rol == "SUPERVISOR":
                # Reasignación opcional desde el form
                if asesor_email:
                    tarea_service.asignar_a_asesor(tarea_id, asesor_email, vencimiento=vencimiento)

            messages.success(request, "Tarea actualizada.")
            return redirect("tareas_listar")

        except Exception as e:
            messages.error(request, str(e))
            # Re-cargar para que la vista muestre el estado real si algo falló
            tarea = tarea_service.obtener_por_id(tarea_id) or tarea

    asesores_activos = AsesorService(DjangoAsesorRepository()).listar_activos()
    asesores = [a for a in asesores_activos if a.rol == "ASESOR"]
    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
        'estados': list(EstadoTarea),
        'prioridades': list(PrioridadTarea),
        'tarea': tarea,
        'asesores': asesores,
    }
    return render(request, 'tareas/editar.html', context)
    
def eliminar_tarea_view(request, tarea_id):
    """
    Elimina una tarea
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    tarea_service = TareaService(DjangoTareaRepository(), asesor_repo=DjangoAsesorRepository())

    if request.method == "POST":
        deleted = DjangoTareaRepository().eliminar(tarea_id)
        if deleted:
            messages.success(request, "Tarea eliminada.")
        else:
            messages.error(request, "No se pudo eliminar la tarea.")
        return redirect("tareas_listar")

    tarea = tarea_service.obtener_por_id(tarea_id)
    if tarea is None:
        messages.error(request, f"No existe la tarea {tarea_id}")
        return redirect("tareas_listar")

    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
        'tarea': tarea,
    }
    return render(request, 'tareas/eliminar.html', context)
    
def reportes_tareas_view(request):
    """
    Muestra reportes estadísticos de tareas (solo ADMIN)
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    # Solo SUPERVISOR (según el sidebar)
    if request.session.get("asesor_rol") != "SUPERVISOR":
        messages.error(request, "No tienes permisos para ver reportes.")
        return redirect("tareas_listar")

    reporte_service = ReporteTareasService(
        DjangoTareaRepository(),
        asesor_repo=DjangoAsesorRepository(),
    )
    estadisticas = reporte_service.generar_resumen_global()

    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
        'estadisticas': estadisticas,
    }
    return render(request, 'tareas/reportes.html', context)