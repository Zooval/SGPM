# Importar todos los modelos desde infrastructure
from SGPM.infrastructure.models import (
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

__all__ = [
    'Solicitante',
    'Asesor',
    'SolicitudMigratoria',
    'Documento',
    'Tarea',
    'Cita',
    'Notificacion',
    'HistorialEstadoSolicitud',
    'HistorialFechaProceso',
]
