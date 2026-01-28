"""
Data Transfer Objects (DTOs) para la capa de aplicación.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict


@dataclass
class SolicitanteDTO:
    """DTO para transferir datos de solicitante"""
    cedula: str
    nombres: str
    apellidos: str
    correo: str
    telefono: str
    direccion: str = ""
    fecha_nacimiento: Optional[date] = None
    habilitado: bool = True

    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"


@dataclass
class AsesorDTO:
    """DTO para transferir datos de asesor"""
    nombres: str
    apellidos: str
    email: str
    rol: str  # "ASESOR", "ADMIN", "OPERADOR"

    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"


@dataclass
class SolicitudMigratoriaDTO:
    """DTO para transferir datos de solicitud migratoria"""
    codigo: str
    tipo_servicio: str  # "VISA_TURISMO", "VISA_TRABAJO", "ESTUDIOS", "RESIDENCIA"
    estado_actual: str  # Estados del enum EstadoSolicitud
    fecha_creacion: datetime
    fecha_expiracion: Optional[datetime] = None
    solicitante_cedula: Optional[str] = None
    asesor_email: Optional[str] = None
    fechas_proceso: Dict[str, Optional[str]] = field(default_factory=dict)


@dataclass
class DocumentoDTO:
    """DTO para transferir datos de documento"""
    id_documento: str
    tipo: str  # Tipos del enum TipoDocumento
    estado: str = "RECIBIDO"  # Estados del enum EstadoDocumento
    fecha_expiracion: Optional[date] = None
    version_actual: int = 1
    observacion: str = ""
    solicitud_codigo: Optional[str] = None


@dataclass
class TareaDTO:
    """DTO para transferir datos de tarea"""
    id_tarea: str
    titulo: str
    prioridad: str  # "BAJA", "MEDIA", "ALTA", "CRITICA"
    estado: str = "PENDIENTE"  # Estados del enum EstadoTarea
    vencimiento: Optional[datetime] = None
    comentario: str = ""
    asesor_email: Optional[str] = None
    solicitud_codigo: Optional[str] = None


@dataclass
class CitaDTO:
    """DTO para transferir datos de cita"""
    id_cita: str
    solicitud_codigo: str
    tipo: str  # "CONSULAR", "BIOMETRIA", "ENTREGA_DOCUMENTOS", "ASESORIA"
    estado: str = "PROGRAMADA"  # Estados del enum EstadoCita
    inicio: Optional[datetime] = None
    fin: Optional[datetime] = None
    observacion: str = ""


@dataclass
class NotificacionDTO:
    """DTO para transferir datos de notificación"""
    id_notificacion: str
    destinatario: str
    tipo: str  # Tipos del enum TipoNotificacion
    mensaje: str
    creada_en: Optional[datetime] = None
    leida: bool = False


@dataclass
class FiltroReporteTareasDTO:
    """DTO para filtros de reporte de tareas"""
    desde: datetime
    hasta: datetime
    asesor_email: Optional[str] = None


@dataclass
class EstadisticasTareasDTO:
    """DTO para estadísticas de tareas"""
    total_tareas: int = 0
    por_estado: Dict[str, int] = field(default_factory=dict)
    por_prioridad: Dict[str, int] = field(default_factory=dict)
    vencidas_total: int = 0
    vencidas_por_asesor: Dict[str, int] = field(default_factory=dict)
    completadas_por_asesor: Dict[str, int] = field(default_factory=dict)


@dataclass
class ReporteTareasDTO:
    """DTO para reporte de tareas"""
    id_reporte: str
    creado_en: datetime
    filtro: FiltroReporteTareasDTO
    estadisticas: EstadisticasTareasDTO
    formato_exportacion: Optional[str] = None  # "PDF", "EXCEL", "JSON"
