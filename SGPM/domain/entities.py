from __future__ import annotations

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
from .value_objects import RangoFechaHora, FiltroReporteTareas, EstadisticasTareas


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
class Solicitante:
    """Representa al solicitante/migrante según el diagrama"""

    def __init__(self, cedula, nombres, apellidos, correo, telefono, fecha_nacimiento=None,
                 direccion: str = "", habilitado: bool = True):
        # Atributos privados para compatibilidad con métodos getter
        self._cedula = cedula
        self._nombres = nombres
        self._apellidos = apellidos
        self._correo = correo
        self._telefono = telefono
        self._fecha_nacimiento = fecha_nacimiento
        self._direccion = direccion
        self._habilitado = habilitado

        # Atributos públicos para acceso directo (manejo_datos_solicitantes.py)
        self.cedula = cedula
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.telefono = telefono
        self.fecha_nacimiento = fecha_nacimiento
        self.direccion = direccion
        self.habilitado = habilitado

        # Relación UML: Solicitante tiene varios documentos
        self._documentos: List["Documento"] = []

    def existe(self):
        """Verifica si el solicitante está registrado correctamente"""
        return self._cedula is not None and len(self._cedula) > 0

    def obtener_cedula(self):
        """Retorna la cédula del solicitante"""
        return self._cedula

    def obtener_correo(self):
        """Retorna el correo del solicitante"""
        return self._correo

    def obtener_nombre_completo(self):
        """Retorna el nombre completo del solicitante"""
        return f"{self._nombres} {self._apellidos}"

    def agregar_documento(self, documento: "Documento") -> None:
        self._documentos.append(documento)

    def obtener_documentos(self) -> List["Documento"]:
        return self._documentos


class Asesor:
    """Representa un asesor según el diagrama UML"""

    def __init__(self, nombres: str, apellidos: str, emailAsesor: str = None, email_asesor: str = None,
                 rol: RolUsuario = RolUsuario.ASESOR):
        self.nombres = nombres
        self.apellidos = apellidos
        # Soportar ambos formatos para compatibilidad
        self.email_asesor = email_asesor or emailAsesor
        self.emailAsesor = self.email_asesor  # Alias para compatibilidad
        self.rol = rol
        self._tareas_asignadas: List["Tarea"] = []

    def asignar_tarea(self, tarea: "Tarea") -> None:
        """Asigna una tarea a este asesor"""
        if tarea not in self._tareas_asignadas:
            self._tareas_asignadas.append(tarea)

    def obtener_tareas(self) -> List["Tarea"]:
        """Retorna la lista de tareas asignadas al asesor"""
        return self._tareas_asignadas.copy()

    def tiene_tarea(self, id_tarea: str) -> bool:
        """Verifica si el asesor tiene asignada una tarea específica"""
        return any(t.idTarea == id_tarea for t in self._tareas_asignadas)

    def obtener_nombre_completo(self) -> str:
        """Retorna el nombre completo del asesor"""
        return f"{self.nombres} {self.apellidos}"


class Documento:
    """Representa un documento según el diagrama"""

    def __init__(self, id_documento, tipo, estado=EstadoDocumento.RECIBIDO,
                 fecha_expiracion=None, version_actual=1, observacion=""):
        self._id = id_documento
        self._tipo = tipo
        self._estado = estado
        self._fecha_expiracion = fecha_expiracion
        self._version_actual = version_actual
        self._observacion = observacion

        # Atributos públicos para acceso directo (BDD steps)
        self.id_documento = id_documento
        self.tipo = tipo
        self.estado = estado
        self.fecha_expiracion = fecha_expiracion
        self.version_actual = version_actual
        self.observacion = observacion

    def obtener_tipo(self):
        """Retorna el tipo del documento"""
        return self._tipo

    def obtener_id(self):
        """Retorna el ID del documento"""
        return self._id

    def marcar_como_rechazado(self, observacion):
        """Marca el documento como rechazado con una observación"""
        self._estado = EstadoDocumento.RECHAZADO
        self._observacion = observacion
        self.estado = EstadoDocumento.RECHAZADO
        self.observacion = observacion

    def marcar_como_aprobado(self):
        """Marca el documento como aprobado"""
        self._estado = EstadoDocumento.APROBADO
        self.estado = EstadoDocumento.APROBADO

    def esta_rechazado(self):
        """Verifica si el documento está rechazado"""
        return self._estado == EstadoDocumento.RECHAZADO

    def esta_aprobado(self):
        """Verifica si el documento está aprobado"""
        return self._estado == EstadoDocumento.APROBADO

    def tiene_observacion(self):
        """Verifica si el documento tiene observación registrada"""
        return self._observacion is not None and len(self._observacion) > 0


class Cita:
    """Representa una cita según el diagrama"""

    def __init__(self, id_cita: str, observacion: str, rango: RangoFechaHora,
                 tipo: TipoCita, estado: EstadoCita, solicitud_codigo: str = None,
                 # Alias para compatibilidad
                 idCita: str = None, solicitudCodigo: str = None):
        # Soportar ambos formatos
        self.id_cita = id_cita or idCita
        self.idCita = self.id_cita  # Alias para compatibilidad
        self.solicitud_codigo = solicitud_codigo or solicitudCodigo
        self.solicitudCodigo = self.solicitud_codigo  # Alias para compatibilidad
        self.observacion = observacion
        self.rango = rango
        self.tipo = tipo
        self.estado = estado


class Tarea:
    """Representa una tarea según el diagrama UML"""

    def __init__(self, idTarea: str = None, titulo: str = None, prioridad: PrioridadTarea = None,
                 vencimiento: Optional[datetime] = None, comentario: str = "",
                 estado: EstadoTarea = EstadoTarea.PENDIENTE,
                 asignadaA: Optional[Asesor] = None,
                 # Aliases en snake_case
                 id_tarea: str = None, asignada_a: Optional[Asesor] = None):
        # Soportar ambos formatos
        self.id_tarea = id_tarea or idTarea
        self.idTarea = self.id_tarea  # Alias para compatibilidad
        self.titulo = titulo
        self.prioridad = prioridad
        self.vencimiento = vencimiento
        self.comentario = comentario
        self.estado = estado
        self.asignada_a = asignada_a or asignadaA
        self.asignadaA = self.asignada_a  # Alias para compatibilidad

    def asignar_a_asesor(self, asesor: Asesor) -> None:
        """Asigna la tarea a un asesor"""
        self.asignadaA = asesor
        asesor.asignar_tarea(self)

    def cambiar_estado(self, nuevo_estado: EstadoTarea) -> None:
        """Cambia el estado de la tarea con validación de transiciones"""
        from .exceptions import TransicionEstadoTareaNoPermitida

        transiciones_validas = {
            EstadoTarea.PENDIENTE: {EstadoTarea.EN_PROGRESO, EstadoTarea.CANCELADA},
            EstadoTarea.EN_PROGRESO: {EstadoTarea.COMPLETADA, EstadoTarea.CANCELADA, EstadoTarea.PENDIENTE},
            EstadoTarea.COMPLETADA: set(),
            EstadoTarea.CANCELADA: {EstadoTarea.PENDIENTE}
        }

        if nuevo_estado not in transiciones_validas.get(self.estado, set()):
            raise TransicionEstadoTareaNoPermitida(
                f"No se puede cambiar de {self.estado.value} a {nuevo_estado.value}"
            )

        self.estado = nuevo_estado

    def actualizar_prioridad(self, nueva_prioridad: PrioridadTarea) -> None:
        """Actualiza la prioridad de la tarea"""
        self.prioridad = nueva_prioridad

    def establecer_vencimiento(self, fecha_vencimiento: datetime) -> None:
        """Establece la fecha de vencimiento de la tarea"""
        self.vencimiento = fecha_vencimiento

    def esta_asignada(self) -> bool:
        """Verifica si la tarea está asignada a algún asesor"""
        return self.asignadaA is not None

    def esta_completada(self) -> bool:
        """Verifica si la tarea está completada"""
        return self.estado == EstadoTarea.COMPLETADA

    def esta_vencida(self) -> bool:
        """Verifica si la tarea está vencida"""
        if self.vencimiento is None:
            return False
        return datetime.now() > self.vencimiento and not self.esta_completada()

    def requiere_recordatorio(self) -> bool:
        """Verifica si la tarea requiere un recordatorio (24 horas antes del vencimiento)"""
        if self.vencimiento is None or self.esta_completada():
            return False

        from datetime import timedelta
        tiempo_restante = self.vencimiento - datetime.now()
        return timedelta(hours=0) <= tiempo_restante <= timedelta(hours=24)


class Notificacion:
    """Representa una notificación según el diagrama"""

    def __init__(self, id_notificacion, destinatario, tipo, mensaje, creada_en: Optional[datetime] = None):
        self.id_notificacion = id_notificacion
        self._id = id_notificacion  # Alias para compatibilidad
        self.destinatario = destinatario
        self._destinatario = destinatario  # Alias para compatibilidad
        self.tipo = tipo
        self._tipo = tipo  # Alias para compatibilidad
        self.mensaje = mensaje
        self._mensaje = mensaje  # Alias para compatibilidad
        self.creada_en = creada_en or datetime.now()
        self._creada_en = self.creada_en  # Alias para compatibilidad
        self._leida = False

    def fue_creada(self):
        """Verifica si la notificación fue creada correctamente"""
        return self._id is not None and self._mensaje is not None

    def obtener_destinatario(self) -> str:
        """Retorna el destinatario de la notificación"""
        return self._destinatario

    def obtener_tipo(self) -> TipoNotificacion:
        """Retorna el tipo de notificación"""
        return self._tipo

    def obtener_mensaje(self) -> str:
        """Retorna el mensaje de la notificación"""
        return self._mensaje

    def marcar_como_leida(self) -> None:
        """Marca la notificación como leída"""
        self._leida = True

    def esta_leida(self) -> bool:
        """Verifica si la notificación fue leída"""
        return self._leida

    @staticmethod
    def crear_notificacion_asignacion_tarea(id_notificacion: str, asesor: Asesor, tarea: "Tarea") -> "Notificacion":
        """Crea una notificación de asignación de tarea"""
        mensaje = f"Se te ha asignado la tarea '{tarea.titulo}' con prioridad {tarea.prioridad.value}"
        return Notificacion(
            id_notificacion=id_notificacion,
            destinatario=asesor.emailAsesor,
            tipo=TipoNotificacion.ASIGNACION_TAREA,
            mensaje=mensaje
        )

    @staticmethod
    def crear_recordatorio_vencimiento(id_notificacion: str, asesor: Asesor, tarea: "Tarea") -> "Notificacion":
        """Crea un recordatorio de vencimiento de tarea"""
        mensaje = f"Recordatorio: La tarea '{tarea.titulo}' vence el {tarea.vencimiento.strftime('%Y-%m-%d')}"
        return Notificacion(
            id_notificacion=id_notificacion,
            destinatario=asesor.emailAsesor,
            tipo=TipoNotificacion.RECORDATORIO,
            mensaje=mensaje
        )


class SolicitudMigratoria:
    """Representa la solicitud migratoria según el diagrama"""

    def __init__(self, codigo: str, tipoServicio: Optional[TipoServicio] = None,
                 estadoActual: Optional[EstadoSolicitud] = None,
                 fechaCreación: Optional[datetime] = None, fechaExpiracion: Optional[datetime] = None,
                 solicitante: Optional[Solicitante] = None, asesor: Optional[Asesor] = None,
                 # Aliases para compatibilidad
                 tipo_servicio: Optional[TipoServicio] = None, estado_actual: Optional[EstadoSolicitud] = None,
                 fecha_creacion: Optional[datetime] = None, fecha_expiracion: Optional[datetime] = None):
        # -------------------------
        # Atributos principales (compatibilidad con ambos formatos)
        # -------------------------
        self._codigo = codigo
        self._tipo_servicio = tipoServicio or tipo_servicio
        self._estado_actual = estadoActual or estado_actual or EstadoSolicitud.CREADA
        self._fecha_creacion = fechaCreación or fecha_creacion or datetime.now()
        self._fecha_expiracion = fechaExpiracion or fecha_expiracion or datetime.now()

        # -------------------------
        # Relaciones UML
        # -------------------------
        self._solicitante = solicitante
        self._asesor = asesor
        self._citas: List[Cita] = []
        self._tareas: List[Tarea] = []
        self._notificaciones: List[Notificacion] = []
        self._documentos: List[Documento] = []
        self._documentos_requeridos: List[TipoDocumento] = []

        # -------------------------
        # Interno para BDD
        # -------------------------
        self._historial_estados: List[Dict[str, Any]] = []
        self._historial_fechas: List[Dict[str, Any]] = []
        self._fechas_proceso: Dict[str, Optional[str]] = {
            "fechaCreacion": self._fecha_creacion.date().isoformat(),
            "fechaUltimaActualizacion": self._fecha_creacion.date().isoformat(),
            "fechaRecepcionDocs": None,
            "fechaEnvioSolicitud": None,
            "fechaCita": None,
        }

    # =====================================================
    # Vincular relaciones
    # =====================================================
    def asignar_solicitante(self, solicitante: Solicitante) -> None:
        self._solicitante = solicitante

    def asignar_asesor(self, asesor: Asesor) -> None:
        self._asesor = asesor

    def agregar_cita(self, cita: Cita) -> None:
        self._citas.append(cita)

    def agregar_tarea(self, tarea: Tarea) -> None:
        self._tareas.append(tarea)

    def agregar_notificacion(self, notificacion: Notificacion) -> None:
        self._notificaciones.append(notificacion)

    # =====================================================
    # Propiedades de acceso
    # =====================================================
    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def estadoActual(self) -> EstadoSolicitud:
        return self._estado_actual

    @estadoActual.setter
    def estadoActual(self, valor: EstadoSolicitud) -> None:
        self._estado_actual = valor

    @property
    def fechaCreación(self) -> datetime:
        return self._fecha_creacion

    @property
    def tipoServicio(self) -> Optional[TipoServicio]:
        return self._tipo_servicio

    # =====================================================
    # Estados y transiciones (BDD)
    # =====================================================
    def _transiciones_permitidas(self) -> Dict[EstadoSolicitud, set[EstadoSolicitud]]:
        return {
            EstadoSolicitud.CREADA: {
                EstadoSolicitud.EN_REVISION,
                EstadoSolicitud.CERRADA,
            },
            EstadoSolicitud.EN_REVISION: {
                EstadoSolicitud.DOCUMENTOS_PENDIENTES,
                EstadoSolicitud.ENVIADA,
                EstadoSolicitud.RECHAZADA,
                EstadoSolicitud.CERRADA,
            },
            EstadoSolicitud.DOCUMENTOS_PENDIENTES: {
                EstadoSolicitud.EN_REVISION,
                EstadoSolicitud.CERRADA,
            },
            EstadoSolicitud.ENVIADA: {
                EstadoSolicitud.APROBADA,
                EstadoSolicitud.RECHAZADA,
                EstadoSolicitud.CERRADA,
            },
            EstadoSolicitud.APROBADA: {EstadoSolicitud.CERRADA},
            EstadoSolicitud.RECHAZADA: {EstadoSolicitud.CERRADA},
            EstadoSolicitud.CERRADA: set(),
        }

    def transicion_permitida(self, nuevo: EstadoSolicitud) -> bool:
        return nuevo in self._transiciones_permitidas().get(
            self._estado_actual, set()
        )

    def cambiar_estado(self, *, nuevo: EstadoSolicitud, usuario: str, motivo: str,
                       fecha_evento: Optional[datetime] = None, ) -> None:
        # Validar que no se cambie desde estado CERRADA (equivalente a Archivada)
        if self._estado_actual == EstadoSolicitud.CERRADA:
            raise TransicionEstadoNoPermitida(
                "No se permiten cambios en Archivada"
            )

        # Validar motivo obligatorio para rechazar
        if nuevo == EstadoSolicitud.RECHAZADA and (not motivo or motivo.strip() == ""):
            raise TransicionEstadoNoPermitida(
                "El motivo es obligatorio al rechazar"
            )

        if not self.transicion_permitida(nuevo):
            raise TransicionEstadoNoPermitida(
                "No se permite la transición solicitada"
            )

        fecha_evento = fecha_evento or datetime.utcnow()
        anterior = self._estado_actual
        self._estado_actual = nuevo

        self._fechas_proceso["fechaUltimaActualizacion"] = (
            fecha_evento.date().isoformat()
        )

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
        return sorted(
            self._historial_estados,
            key=lambda x: x["fecha"],
            reverse=True,
        )

    # =====================================================
    # Fechas del proceso (BDD)
    # =====================================================
    def _campos_fecha_permitidos(self) -> set[str]:
        return {"fechaRecepcionDocs", "fechaEnvioSolicitud", "fechaCita"}

    def asignar_fecha_proceso(self, *, campo: str, valor_iso: str, usuario: str,
                              fecha_evento: Optional[datetime] = None, ) -> None:
        if campo not in self._campos_fecha_permitidos():
            raise CampoFechaNoPermitido(f"Campo no permitido: {campo}")

        fecha_evento = fecha_evento or datetime.utcnow()
        valor_date = parse_date_iso(valor_iso)

        if valor_date < self._fecha_creacion.date():
            raise FechaInvalida(
                "La fecha no puede ser anterior a la fecha de creación"
            )

        # Validar coherencia: fechaEnvioSolicitud no puede ser anterior a fechaRecepcionDocs
        if campo == "fechaEnvioSolicitud":
            fecha_recepcion = self._fechas_proceso.get("fechaRecepcionDocs")
            if fecha_recepcion is not None:
                fecha_recepcion_date = parse_date_iso(fecha_recepcion)
                if valor_date < fecha_recepcion_date:
                    raise FechaInvalida(
                        "La fecha de envío no puede ser anterior a la recepción de documentos"
                    )

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
        return {
            "fechaCreacion": self._fechas_proceso.get("fechaCreacion"),
            "fechaUltimaActualizacion": self._fechas_proceso.get("fechaUltimaActualizacion"),
            "fechaRecepcionDocs": self._fechas_proceso.get("fechaRecepcionDocs"),
            "fechaEnvioSolicitud": self._fechas_proceso.get("fechaEnvioSolicitud"),
            "fechaCita": self._fechas_proceso.get("fechaCita"),
        }

    def obtener_historial_fechas(self) -> List[Dict[str, Any]]:
        return sorted(
            self._historial_fechas,
            key=lambda x: x["fecha"],
            reverse=True,
        )

    # =====================================================
    # Documentos (flujo operativo)
    # =====================================================
    def tiene_proceso_activo(self) -> bool:
        """Verifica si existe un proceso de visa activo"""
        return self._codigo is not None

    def agregar_documento(self, documento: "Documento") -> None:
        """Añade un documento a la solicitud"""
        self._documentos.append(documento)

    def obtener_documentos(self):
        """Retorna la lista de documentos"""
        return self._documentos

    def obtener_documentos_faltantes(self):
        """Retorna lista de tipos de documentos que faltan"""
        tipos_presentes = {doc.obtener_tipo() for doc in self._documentos}
        return [
            tipo
            for tipo in self._documentos_requeridos
            if tipo not in tipos_presentes
        ]

    def tiene_documentos_faltantes(self) -> bool:
        """Verifica si faltan documentos requeridos"""
        return len(self.obtener_documentos_faltantes()) > 0

    def esta_completa(self) -> bool:
        """Valida que todos los documentos requeridos estén presentes y aprobados"""
        if self.tiene_documentos_faltantes():
            return False
        return all(doc.esta_aprobado() for doc in self._documentos)

    # =====================================================
    # Estado (consultas simples)
    # =====================================================
    def esta_en_revision(self) -> bool:
        """Verifica si la solicitud está en revisión"""
        return self._estado_actual == EstadoSolicitud.EN_REVISION

    def tiene_documentos_pendientes(self) -> bool:
        """Verifica si el estado es DOCUMENTOS_PENDIENTES"""
        return self._estado_actual == EstadoSolicitud.DOCUMENTOS_PENDIENTES

    def documentos_fueron_registrados(self, cantidad_esperada: int) -> bool:
        """Verifica si la cantidad de documentos registrados coincide"""
        return len(self._documentos) == cantidad_esperada


class ReporteTareas:
    """Representa un reporte de tareas según el diagrama UML"""

    def __init__(self, id_reporte: str, creado_en: datetime, filtro: FiltroReporteTareas,
                 estadisticas: EstadisticasTareas):
        self.id_reporte = id_reporte
        self.creado_en = creado_en
        self.filtro = filtro
        self.estadisticas = estadisticas

    def obtener_id(self) -> str:
        """Retorna el ID del reporte"""
        return self.id_reporte

    def obtener_fecha_creacion(self) -> datetime:
        """Retorna la fecha de creación del reporte"""
        return self.creado_en

    def obtener_filtro(self) -> FiltroReporteTareas:
        """Retorna el filtro aplicado al reporte"""
        return self.filtro

    def obtener_estadisticas(self) -> EstadisticasTareas:
        """Retorna las estadísticas del reporte"""
        return self.estadisticas
