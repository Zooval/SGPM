"""
Módulo de dominio - Contiene las entidades, value objects, enums, excepciones y repositorios abstractos.
"""
from .entities import (
    Solicitante,
    Asesor,
    Documento,
    Cita,
    Tarea,
    Notificacion,
    SolicitudMigratoria,
)
from .enums import (
    RolUsuario,
    EstadoSolicitud,
    TipoServicio,
    TipoDocumento,
    EstadoDocumento,
    EstadoTarea,
    PrioridadTarea,
    TipoCita,
    EstadoCita,
    TipoNotificacion,
)
from .exceptions import (
    DomainError,
    EstadoSolicitudInvalidoError,
    DocumentoInvalidoError,
    DocumentoExpiradoError,
    CitaInvalidaError,
    ReglaNegocioError,
    TareaYaAsignadaError,
    TransicionEstadoTareaNoPermitida,
    TareaNoEncontradaError,
)
from .repositories import (
    SolicitanteRepository,
    AsesorRepository,
    SolicitudMigratoriaRepository,
    DocumentoRepository,
    TareaRepository,
    CitaRepository,
    NotificacionRepository,
)
from .value_objects import RangoFechaHora

__all__ = [
    # Entities
    "Solicitante",
    "Asesor",
    "Documento",
    "Cita",
    "Tarea",
    "Notificacion",
    "SolicitudMigratoria",
    # Enums
    "RolUsuario",
    "EstadoSolicitud",
    "TipoServicio",
    "TipoDocumento",
    "EstadoDocumento",
    "EstadoTarea",
    "PrioridadTarea",
    "TipoCita",
    "EstadoCita",
    "TipoNotificacion",
    # Exceptions
    "DomainError",
    "EstadoSolicitudInvalidoError",
    "DocumentoInvalidoError",
    "DocumentoExpiradoError",
    "CitaInvalidaError",
    "ReglaNegocioError",
    "TareaYaAsignadaError",
    "TransicionEstadoTareaNoPermitida",
    "TareaNoEncontradaError",
    # Repositories
    "SolicitanteRepository",
    "AsesorRepository",
    "SolicitudMigratoriaRepository",
    "DocumentoRepository",
    "TareaRepository",
    "CitaRepository",
    "NotificacionRepository",
    # Value Objects
    "RangoFechaHora",
]
