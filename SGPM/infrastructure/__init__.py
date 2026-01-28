"""
Módulo de infraestructura - Contiene los modelos Django y repositorios concretos.
"""
from .models import (
    Solicitante,
    Asesor,
    SolicitudMigratoria,
    Documento,
    Tarea,
    Cita,
    Notificacion,
    HistorialEstadoSolicitud,
    HistorialFechaProceso,
)
from .repositories import (
    DjangoSolicitanteRepository,
    DjangoAsesorRepository,
    DjangoSolicitudMigratoriaRepository,
    DjangoDocumentoRepository,
    DjangoTareaRepository,
    DjangoCitaRepository,
    DjangoNotificacionRepository,
)

__all__ = [
    # Models
    "Solicitante",
    "Asesor",
    "SolicitudMigratoria",
    "Documento",
    "Tarea",
    "Cita",
    "Notificacion",
    "HistorialEstadoSolicitud",
    "HistorialFechaProceso",
    # Repositories
    "DjangoSolicitanteRepository",
    "DjangoAsesorRepository",
    "DjangoSolicitudMigratoriaRepository",
    "DjangoDocumentoRepository",
    "DjangoTareaRepository",
    "DjangoCitaRepository",
    "DjangoNotificacionRepository",
]
