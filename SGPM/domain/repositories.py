"""
Repositorios abstractos del dominio.
Definen los contratos/interfaces que deben implementar los repositorios concretos.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List

from .entities import (
    Solicitante,
    Asesor,
    SolicitudMigratoria,
    Documento,
    Tarea,
    Cita,
    Notificacion,
)
from .enums import (
    EstadoSolicitud,
    EstadoDocumento,
    EstadoTarea,
    EstadoCita,
    TipoDocumento,
    TipoCita,
    PrioridadTarea,
)


# ========================================
# Repositorio: Solicitante
# ========================================
class SolicitanteRepository(ABC):
    """Repositorio abstracto para Solicitante"""

    @abstractmethod
    def guardar(self, solicitante: Solicitante) -> Solicitante:
        """Guarda o actualiza un solicitante"""
        pass

    @abstractmethod
    def obtener_por_cedula(self, cedula: str) -> Optional[Solicitante]:
        """Obtiene un solicitante por su cédula"""
        pass

    @abstractmethod
    def obtener_por_correo(self, correo: str) -> Optional[Solicitante]:
        """Obtiene un solicitante por su correo electrónico"""
        pass

    @abstractmethod
    def listar_todos(self) -> List[Solicitante]:
        """Lista todos los solicitantes"""
        pass

    @abstractmethod
    def eliminar(self, cedula: str) -> bool:
        """Elimina un solicitante por su cédula"""
        pass

    @abstractmethod
    def existe(self, cedula: str) -> bool:
        """Verifica si existe un solicitante con la cédula dada"""
        pass


# ========================================
# Repositorio: Asesor
# ========================================
class AsesorRepository(ABC):
    """Repositorio abstracto para Asesor"""

    @abstractmethod
    def guardar(self, asesor: Asesor) -> Asesor:
        """Guarda o actualiza un asesor"""
        pass

    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Asesor]:
        """Obtiene un asesor por su email"""
        pass

    @abstractmethod
    def listar_todos(self) -> List[Asesor]:
        """Lista todos los asesores"""
        pass

    @abstractmethod
    def listar_activos(self) -> List[Asesor]:
        """Lista solo los asesores activos"""
        pass

    @abstractmethod
    def eliminar(self, email: str) -> bool:
        """Elimina un asesor por su email"""
        pass

    @abstractmethod
    def existe(self, email: str) -> bool:
        """Verifica si existe un asesor con el email dado"""
        pass


# ========================================
# Repositorio: SolicitudMigratoria
# ========================================
class SolicitudMigratoriaRepository(ABC):
    """Repositorio abstracto para SolicitudMigratoria"""

    @abstractmethod
    def guardar(self, solicitud: SolicitudMigratoria) -> SolicitudMigratoria:
        """Guarda o actualiza una solicitud migratoria"""
        pass

    @abstractmethod
    def obtener_por_codigo(self, codigo: str) -> Optional[SolicitudMigratoria]:
        """Obtiene una solicitud por su código"""
        pass

    @abstractmethod
    def listar_todas(self) -> List[SolicitudMigratoria]:
        """Lista todas las solicitudes"""
        pass

    @abstractmethod
    def listar_por_estado(self, estado: EstadoSolicitud) -> List[SolicitudMigratoria]:
        """Lista solicitudes por estado"""
        pass

    @abstractmethod
    def listar_por_solicitante(self, cedula: str) -> List[SolicitudMigratoria]:
        """Lista solicitudes de un solicitante específico"""
        pass

    @abstractmethod
    def listar_por_asesor(self, email_asesor: str) -> List[SolicitudMigratoria]:
        """Lista solicitudes asignadas a un asesor"""
        pass

    @abstractmethod
    def eliminar(self, codigo: str) -> bool:
        """Elimina una solicitud por su código"""
        pass

    @abstractmethod
    def existe(self, codigo: str) -> bool:
        """Verifica si existe una solicitud con el código dado"""
        pass


# ========================================
# Repositorio: Documento
# ========================================
class DocumentoRepository(ABC):
    """Repositorio abstracto para Documento"""

    @abstractmethod
    def guardar(self, documento: Documento, solicitud_codigo: str) -> Documento:
        """Guarda o actualiza un documento"""
        pass

    @abstractmethod
    def obtener_por_id(self, id_documento: str) -> Optional[Documento]:
        """Obtiene un documento por su ID"""
        pass

    @abstractmethod
    def listar_por_solicitud(self, solicitud_codigo: str) -> List[Documento]:
        """Lista documentos de una solicitud"""
        pass

    @abstractmethod
    def listar_por_estado(self, estado: EstadoDocumento) -> List[Documento]:
        """Lista documentos por estado"""
        pass

    @abstractmethod
    def listar_por_tipo(self, tipo: TipoDocumento) -> List[Documento]:
        """Lista documentos por tipo"""
        pass

    @abstractmethod
    def eliminar(self, id_documento: str) -> bool:
        """Elimina un documento por su ID"""
        pass

    @abstractmethod
    def existe(self, id_documento: str) -> bool:
        """Verifica si existe un documento con el ID dado"""
        pass


# ========================================
# Repositorio: Tarea
# ========================================
class TareaRepository(ABC):
    """Repositorio abstracto para Tarea"""

    @abstractmethod
    def guardar(self, tarea: Tarea) -> Tarea:
        """Guarda o actualiza una tarea"""
        pass

    @abstractmethod
    def obtener_por_id(self, id_tarea: str) -> Optional[Tarea]:
        """Obtiene una tarea por su ID"""
        pass

    @abstractmethod
    def listar_todas(self) -> List[Tarea]:
        """Lista todas las tareas"""
        pass

    @abstractmethod
    def listar_por_estado(self, estado: EstadoTarea) -> List[Tarea]:
        """Lista tareas por estado"""
        pass

    @abstractmethod
    def listar_por_prioridad(self, prioridad: PrioridadTarea) -> List[Tarea]:
        """Lista tareas por prioridad"""
        pass

    @abstractmethod
    def listar_por_asesor(self, email_asesor: str) -> List[Tarea]:
        """Lista tareas asignadas a un asesor"""
        pass

    @abstractmethod
    def listar_por_solicitud(self, solicitud_codigo: str) -> List[Tarea]:
        """Lista tareas de una solicitud"""
        pass

    @abstractmethod
    def listar_vencidas(self) -> List[Tarea]:
        """Lista tareas vencidas"""
        pass

    @abstractmethod
    def listar_por_vencer(self, horas: int = 24) -> List[Tarea]:
        """Lista tareas próximas a vencer en las próximas horas indicadas"""
        pass

    @abstractmethod
    def eliminar(self, id_tarea: str) -> bool:
        """Elimina una tarea por su ID"""
        pass

    @abstractmethod
    def existe(self, id_tarea: str) -> bool:
        """Verifica si existe una tarea con el ID dado"""
        pass


# ========================================
# Repositorio: Cita
# ========================================
class CitaRepository(ABC):
    """Repositorio abstracto para Cita"""

    @abstractmethod
    def guardar(self, cita: Cita) -> Cita:
        """Guarda o actualiza una cita"""
        pass

    @abstractmethod
    def obtener_por_id(self, id_cita: str) -> Optional[Cita]:
        """Obtiene una cita por su ID"""
        pass

    @abstractmethod
    def listar_todas(self) -> List[Cita]:
        """Lista todas las citas"""
        pass

    @abstractmethod
    def listar_por_estado(self, estado: EstadoCita) -> List[Cita]:
        """Lista citas por estado"""
        pass

    @abstractmethod
    def listar_por_tipo(self, tipo: TipoCita) -> List[Cita]:
        """Lista citas por tipo"""
        pass

    @abstractmethod
    def listar_por_solicitud(self, solicitud_codigo: str) -> List[Cita]:
        """Lista citas de una solicitud"""
        pass

    @abstractmethod
    def listar_por_rango_fecha(self, inicio: datetime, fin: datetime) -> List[Cita]:
        """Lista citas en un rango de fechas"""
        pass

    @abstractmethod
    def verificar_disponibilidad(self, inicio: datetime, fin: datetime) -> bool:
        """Verifica si hay disponibilidad en el horario indicado"""
        pass

    @abstractmethod
    def eliminar(self, id_cita: str) -> bool:
        """Elimina una cita por su ID"""
        pass

    @abstractmethod
    def existe(self, id_cita: str) -> bool:
        """Verifica si existe una cita con el ID dado"""
        pass


# ========================================
# Repositorio: Notificacion
# ========================================
class NotificacionRepository(ABC):
    """Repositorio abstracto para Notificacion"""

    @abstractmethod
    def guardar(self, notificacion: Notificacion) -> Notificacion:
        """Guarda una notificación"""
        pass

    @abstractmethod
    def obtener_por_id(self, id_notificacion: str) -> Optional[Notificacion]:
        """Obtiene una notificación por su ID"""
        pass

    @abstractmethod
    def listar_por_destinatario(self, destinatario: str) -> List[Notificacion]:
        """Lista notificaciones por destinatario"""
        pass

    @abstractmethod
    def listar_no_leidas(self, destinatario: str) -> List[Notificacion]:
        """Lista notificaciones no leídas de un destinatario"""
        pass

    @abstractmethod
    def marcar_como_leida(self, id_notificacion: str) -> bool:
        """Marca una notificación como leída"""
        pass

    @abstractmethod
    def eliminar(self, id_notificacion: str) -> bool:
        """Elimina una notificación por su ID"""
        pass

    @abstractmethod
    def existe(self, id_notificacion: str) -> bool:
        """Verifica si existe una notificación con el ID dado"""
        pass
