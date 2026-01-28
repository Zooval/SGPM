from __future__ import annotations
from enum import Enum


class RolUsuario(str, Enum):
    ASESOR = "ASESOR"
    SUPERVISOR = "SUPERVISOR"


class EstadoSolicitud(Enum):
    CREADA = "Creada"
    EN_REVISION = "En revision"
    DOCUMENTOS_PENDIENTES = "Documentos pendientes"
    ENVIADA = "Enviada"
    APROBADA = "Aprobada"
    RECHAZADA = "Rechazada"
    CERRADA = "Cerrada"
    ARCHIVADA = "Archivada"  # requerido por tu feature


class TipoServicio(str, Enum):
    VISA_TURISMO = "VISA_TURISMO"
    VISA_TRABAJO = "VISA_TRABAJO"
    ESTUDIOS = "ESTUDIOS"
    RESIDENCIA = "RESIDENCIA"


class TipoDocumento(str, Enum):
    PASAPORTE = "PASAPORTE"
    ANTECEDENTES = "ANTECEDENTES"
    ESTADOS_BANCARIOS = "ESTADOS_BANCARIOS"
    CONTRATO_TRABAJO = "CONTRATO_TRABAJO"
    MATRICULA_ESTUDIOS = "MATRICULA_ESTUDIOS"
    OTROS = "OTROS"


class EstadoDocumento(str, Enum):
    RECIBIDO = "RECIBIDO"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    VENCIDO = "VENCIDO"


class EstadoTarea(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"


class PrioridadTarea(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class TipoCita(str, Enum):
    CONSULAR = "CONSULAR"
    BIOMETRIA = "BIOMETRIA"
    ENTREGA_DOCUMENTOS = "ENTREGA_DOCUMENTOS"
    ASESORIA = "ASESORIA"


class EstadoCita(str, Enum):
    PROGRAMADA = "PROGRAMADA"
    REPROGRAMADA = "REPROGRAMADA"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"
    NO_ASISTIO = "NO_ASISTIO"


class TipoNotificacion(str, Enum):
    RECORDATORIO = "RECORDATORIO"
    DOC_FALTANTE = "DOC_FALTANTE"
    CITA_PROXIMA = "CITA_PROXIMA"
    ASIGNACION_TAREA = "ASIGNACION_TAREA"
