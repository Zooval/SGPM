from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List, Dict, Any

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
from .value_objects import RangoFechaHora


# =========================
# Excepciones de dominio (para validar escenarios BDD)
# =========================
class DomainError(Exception):
    pass


class TransicionEstadoNoPermitida(DomainError):
    pass


class CampoFechaNoPermitido(DomainError):
    pass


class FechaInvalida(DomainError):
    pass


# =========================
# Helpers (útiles en steps, sin crear nuevas "clases" fuera del UML)
# =========================
def parse_date_iso(value: str) -> date:
    return date.fromisoformat(value.strip())


def parse_datetime_iso(value: str) -> datetime:
    v = value.strip()
    if "T" in v:
        return datetime.fromisoformat(v)
    return datetime.fromisoformat(v + "T00:00:00")


def parse_estado_solicitud(texto: str) -> EstadoSolicitud:
    raw = texto.strip().upper().replace(" ", "_").replace("-", "_")
    equivalencias = {
        "CREADA": "CREADA",
        "EN_REVISION": "EN_REVISION",
        "EN_REVISIÓN": "EN_REVISION",
        "DOCUMENTOS_PENDIENTES": "DOCUMENTOS_PENDIENTES",
        "DOCS_PENDIENTES": "DOCUMENTOS_PENDIENTES",
        "ENVIADA": "ENVIADA",
        "APROBADA": "APROBADA",
        "RECHAZADA": "RECHAZADA",
        "CERRADA": "CERRADA",
        # si tu feature usa "Archivada", tu enum no lo tiene: lo tratamos como CERRADA
        "ARCHIVADA": "CERRADA",
    }
    key = equivalencias.get(raw, raw)
    try:
        return EstadoSolicitud[key]
    except KeyError as e:
        raise ValueError(f"EstadoSolicitud desconocido: '{texto}'") from e


# =========================
# Entidades (UML)
# =========================
@dataclass
class Solicitante:
    cedula: str
    nombres: str
    apellidos: str
    correo: str
    telefono: str
    fechaNacimiento: date

    # Relación UML: Solicitante tiene varios documentos
    documentos: List["Documento"] = field(default_factory=list)

    def agregar_documento(self, documento: "Documento") -> None:
        self.documentos.append(documento)


@dataclass
class Asesor:
    nombres: str
    apellidos: str
    emailAsesor: str
    rol: RolUsuario = RolUsuario.ASESOR


@dataclass
class Documento:
    idDocumento: str
    tipo: TipoDocumento
    estado: EstadoDocumento
    fechaExpiracion: date
    versionActual: int
    observacion: str = ""


@dataclass
class Cita:
    idCita: str
    solicitudCodigo: str
    observacion: str
    rango: RangoFechaHora
    tipo: TipoCita
    estado: EstadoCita


@dataclass
class Tarea:
    idTarea: str
    asignadaA: Asesor            # <- según tu pedido: tarea asignada a asesor
    vencimiento: datetime
    estado: EstadoTarea
    prioridad: PrioridadTarea
    comentario: str
    titulo: str


@dataclass
class Notificacion:
    idNotificacion: str
    destinatario: str            # <- email solo str
    tipo: TipoNotificacion
    mensaje: str
    creadaEn: datetime


@dataclass
class SolicitudMigratoria:
    codigo: str
    tipoServicio: TipoServicio
    estadoActual: EstadoSolicitud
    fechaCreación: datetime
    fechaExpiracion: datetime

    # Relaciones de negocio (UML)
    solicitante: Optional[Solicitante] = None
    asesor: Optional[Asesor] = None
    citas: List[Cita] = field(default_factory=list)
    tareas: List[Tarea] = field(default_factory=list)
    notificaciones: List[Notificacion] = field(default_factory=list)

    # ===== Interno para BDD (sin agregar nuevas "clases")
    _historial_estados: List[Dict[str, Any]] = field(default_factory=list, repr=False)
    _historial_fechas: List[Dict[str, Any]] = field(default_factory=list, repr=False)
    _fechas_proceso: Dict[str, Optional[str]] = field(default_factory=dict, repr=False)  # strings ISO

    def __post_init__(self) -> None:
        # Para tus .feature: fechaUltimaActualizacion debe existir
        self._fechas_proceso.setdefault("fechaCreacion", self.fechaCreación.date().isoformat())
        self._fechas_proceso.setdefault("fechaUltimaActualizacion", self.fechaCreación.date().isoformat())
        self._fechas_proceso.setdefault("fechaRecepcionDocs", None)
        self._fechas_proceso.setdefault("fechaEnvioSolicitud", None)
        self._fechas_proceso.setdefault("fechaCita", None)

    # -------------------------
    # Vincular relaciones
    # -------------------------
    def asignar_solicitante(self, solicitante: Solicitante) -> None:
        self.solicitante = solicitante

    def asignar_asesor(self, asesor: Asesor) -> None:
        self.asesor = asesor

    def agregar_cita(self, cita: Cita) -> None:
        self.citas.append(cita)

    def agregar_tarea(self, tarea: Tarea) -> None:
        self.tareas.append(tarea)

    def agregar_notificacion(self, notificacion: Notificacion) -> None:
        self.notificaciones.append(notificacion)

    # -------------------------
    # Reglas de negocio para BDD: estados + historial + fechaUltimaActualizacion
    # -------------------------
    def _transiciones_permitidas(self) -> Dict[EstadoSolicitud, set[EstadoSolicitud]]:
        return {
            EstadoSolicitud.CREADA: {EstadoSolicitud.EN_REVISION, EstadoSolicitud.CERRADA},
            EstadoSolicitud.EN_REVISION: {
                EstadoSolicitud.DOCUMENTOS_PENDIENTES,
                EstadoSolicitud.ENVIADA,
                EstadoSolicitud.RECHAZADA,
                EstadoSolicitud.CERRADA,
            },
            EstadoSolicitud.DOCUMENTOS_PENDIENTES: {EstadoSolicitud.EN_REVISION, EstadoSolicitud.CERRADA},
            EstadoSolicitud.ENVIADA: {EstadoSolicitud.APROBADA, EstadoSolicitud.RECHAZADA, EstadoSolicitud.CERRADA},
            EstadoSolicitud.APROBADA: {EstadoSolicitud.CERRADA},
            EstadoSolicitud.RECHAZADA: {EstadoSolicitud.CERRADA},
            EstadoSolicitud.CERRADA: set(),
        }

    def transicion_permitida(self, nuevo: EstadoSolicitud) -> bool:
        return nuevo in self._transiciones_permitidas().get(self.estadoActual, set())

    def cambiar_estado(self, *, nuevo: EstadoSolicitud, usuario: str, motivo: str, fecha_evento: Optional[datetime] = None) -> None:
        if not self.transicion_permitida(nuevo):
            raise TransicionEstadoNoPermitida(f"Transición inválida: {self.estadoActual.value} -> {nuevo.value}")

        fecha_evento = fecha_evento or datetime.utcnow()
        anterior = self.estadoActual
        self.estadoActual = nuevo

        # actualizar fechaUltimaActualizacion para tus asserts
        self._fechas_proceso["fechaUltimaActualizacion"] = fecha_evento.date().isoformat()

        # registrar historial (para tabla de tu .feature)
        self._historial_estados.append(
            {
                "usuario": usuario,
                "anterior": anterior.value,
                "nuevo": nuevo.value,
                "fecha": fecha_evento.date().isoformat(),
                "motivo": motivo,
            }
        )

    def obtener_historial_estados(self) -> List[Dict[str, Any]]:
        # orden cronológico descendente (tu feature lo pide)
        return sorted(self._historial_estados, key=lambda x: x["fecha"], reverse=True)

    # -------------------------
    # Fechas del proceso (para BDD): asignación + historial
    # Campos esperados por tu feature:
    # fechaRecepcionDocs, fechaEnvioSolicitud, fechaCita
    # -------------------------
    def _campos_fecha_permitidos(self) -> set[str]:
        return {"fechaRecepcionDocs", "fechaEnvioSolicitud", "fechaCita"}

    def asignar_fecha_proceso(
        self,
        *,
        campo: str,
        valor_iso: str,
        usuario: str,
        fecha_evento: Optional[datetime] = None,
    ) -> None:
        if campo not in self._campos_fecha_permitidos():
            raise CampoFechaNoPermitido(f"Campo no permitido: {campo}")

        fecha_evento = fecha_evento or datetime.utcnow()

        # regla de tu feature: fecha >= fechaCreacion
        valor_date = parse_date_iso(valor_iso)
        if valor_date < self.fechaCreación.date():
            raise FechaInvalida(f"{campo} no puede ser anterior a la fecha de creación")

        anterior = self._fechas_proceso.get(campo)
        self._fechas_proceso[campo] = valor_date.isoformat()

        self._historial_fechas.append(
            {
                "usuario": usuario,
                "campo": campo,
                "valorAnterior": anterior,
                "valorNuevo": valor_date.isoformat(),
                "fecha": fecha_evento.date().isoformat(),
            }
        )

    def obtener_fecha_proceso(self, campo: str) -> Optional[str]:
        return self._fechas_proceso.get(campo)

    def obtener_fechas_clave(self) -> Dict[str, Optional[str]]:
        # exactamente en los nombres del feature (camelCase)
        return {
            "fechaCreacion": self._fechas_proceso.get("fechaCreacion"),
            "fechaUltimaActualizacion": self._fechas_proceso.get("fechaUltimaActualizacion"),
            "fechaRecepcionDocs": self._fechas_proceso.get("fechaRecepcionDocs"),
            "fechaEnvioSolicitud": self._fechas_proceso.get("fechaEnvioSolicitud"),
            "fechaCita": self._fechas_proceso.get("fechaCita"),
        }

    def obtener_historial_fechas(self) -> List[Dict[str, Any]]:
        return sorted(self._historial_fechas, key=lambda x: x["fecha"], reverse=True)
