from __future__ import annotations

import os
from uuid import uuid4
from pathlib import Path
from datetime import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings

from SGPM.application.dtos import DocumentoDTO
from SGPM.application.services import DocumentoService, DocumentoInvalidoError
from SGPM.domain.enums import TipoDocumento, EstadoDocumento
from SGPM.infrastructure.repositories import DjangoDocumentoRepository, DjangoSolicitudMigratoriaRepository


def _require_login(request):
    if not request.session.get("asesor_email"):
        return redirect("login")
    return None


def gestionar_documentos_view(request, codigo: str):
    """
    Permite registrar documentos (PDF) asociados a una solicitud.
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    service = DocumentoService(
        DjangoDocumentoRepository(),
        solicitud_repo=DjangoSolicitudMigratoriaRepository(),
    )

    if request.method == "POST":
        tipo = (request.POST.get("tipo") or "").strip()
        observacion = (request.POST.get("observacion") or "").strip()
        archivo = request.FILES.get("archivo")

        try:
            if not tipo or not archivo:
                messages.error(request, "Tipo de documento y archivo PDF son obligatorios.")
            elif not archivo.name.lower().endswith(".pdf"):
                messages.error(request, "Solo se permiten archivos en formato PDF.")
            else:
                # Guardar metadata en dominio/BD
                dto = DocumentoDTO(
                    id_documento=str(uuid4()),
                    tipo=tipo,
                    estado="RECIBIDO",
                    observacion=observacion,
                    solicitud_codigo=codigo,
                )
                registrado = service.registrar_documento(dto)

                # Guardar archivo físicamente
                base_dir = Path(getattr(settings, "BASE_DIR", Path.cwd()))
                media_root = base_dir / "media" / "documentos"
                os.makedirs(media_root, exist_ok=True)

                filename = f"{registrado.id_documento}.pdf"
                destino = media_root / filename
                with destino.open("wb+") as dest:
                    for chunk in archivo.chunks():
                        dest.write(chunk)

                messages.success(request, "Documento registrado y archivo PDF guardado correctamente.")
                return redirect("solicitud_documentos", codigo=codigo)

        except DocumentoInvalidoError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Ocurrió un error al registrar el documento: {e}")

    # Listar documentos actuales de la solicitud
    documentos = service.listar_por_solicitud(codigo)

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "codigo": codigo,
        "documentos": documentos,
        "tipos_documento": list(TipoDocumento),
    }
    return render(request, "solicitudes/documentos.html", context)


def editar_documento_view(request, id_documento: str):
    """
    Edita metadatos de un documento (estado, fecha de expiración, observación).
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    codigo = request.GET.get("codigo") or request.POST.get("codigo") or ""

    service = DocumentoService(
        DjangoDocumentoRepository(),
        solicitud_repo=DjangoSolicitudMigratoriaRepository(),
    )

    doc = service.obtener_por_id(id_documento)
    if doc is None:
        messages.error(request, "El documento no existe.")
        if codigo:
            return redirect("solicitud_documentos", codigo=codigo)
        return redirect("solicitud_documentos_menu")

    if request.method == "POST":
        estado = (request.POST.get("estado") or doc.estado).strip()
        obs = (request.POST.get("observacion") or "").strip()
        fecha_str = (request.POST.get("fecha_expiracion") or "").strip()
        fecha = None
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Fecha de expiración inválida.")
                return redirect(request.path + f"?codigo={codigo}")

        try:
            if not codigo:
                messages.error(request, "No se encontró el código de la solicitud asociado.")
            else:
                service.actualizar_documento(
                    id_documento,
                    solicitud_codigo=codigo,
                    estado=estado,
                    fecha_expiracion=fecha,
                    observacion=obs,
                )
                messages.success(request, "Documento actualizado correctamente.")
                return redirect("solicitud_documentos", codigo=codigo)
        except DocumentoInvalidoError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Ocurrió un error al actualizar el documento: {e}")

    context = {
        "asesor_nombre": request.session.get("asesor_nombre"),
        "asesor_email": request.session.get("asesor_email"),
        "asesor_rol": request.session.get("asesor_rol"),
        "codigo": codigo,
        "documento": doc,
        "estados": list(EstadoDocumento),
    }
    return render(request, "solicitudes/documento_editar.html", context)


def eliminar_documento_view(request, id_documento: str):
    """
    Elimina un documento (solo metadata; el archivo PDF podría dejarse como histórico).
    """
    redirect_resp = _require_login(request)
    if redirect_resp:
        return redirect_resp

    codigo = request.GET.get("codigo") or request.POST.get("codigo") or ""

    if request.method != "POST":
        if codigo:
            return redirect("solicitud_documentos", codigo=codigo)
        return redirect("solicitud_documentos_menu")

    service = DocumentoService(
        DjangoDocumentoRepository(),
        solicitud_repo=DjangoSolicitudMigratoriaRepository(),
    )
    try:
        ok = service.eliminar_documento(id_documento)
        if ok:
            messages.success(request, "Documento eliminado.")
        else:
            messages.error(request, "No se pudo eliminar el documento.")
    except Exception as e:
        messages.error(request, f"Ocurrió un error al eliminar el documento: {e}")

    if codigo:
        return redirect("solicitud_documentos", codigo=codigo)
    return redirect("solicitud_documentos_menu")


