"""
Servicios de aplicación.
Implementan la lógica de negocio siguiendo los patrones de los steps de BDD.
"""
from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple

from SGPM.domain.entities import (
    Solicitante,
    Asesor,
    SolicitudMigratoria,
    Documento,
    Tarea,
    Cita,
    Notificacion,
)
from SGPM.domain.enums import (
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
from SGPM.domain.value_objects import RangoFechaHora
from SGPM.domain.exceptions import (
    TareaNoEncontradaError,
    CitaInvalidaError,
    DocumentoInvalidoError,
)
from SGPM.domain.repositories import (
    SolicitanteRepository,
    AsesorRepository,
    SolicitudMigratoriaRepository,
    DocumentoRepository,
    TareaRepository,
    CitaRepository,
    NotificacionRepository,
)
from .dtos import (
    SolicitanteDTO,
    AsesorDTO,
    SolicitudMigratoriaDTO,
    DocumentoDTO,
    TareaDTO,
    CitaDTO,
    NotificacionDTO,
    FiltroReporteTareasDTO,
    EstadisticasTareasDTO,
    ReporteTareasDTO,
)


# ============================================================
# Excepciones de Servicio
# ============================================================
class ServiceError(Exception):
    """Error base de servicios"""
    pass


class SolicitanteNoEncontradoError(ServiceError):
    pass


class SolicitanteDuplicadoError(ServiceError):
    pass


class AsesorNoEncontradoError(ServiceError):
    pass


class SolicitudNoEncontradaError(ServiceError):
    pass


class DatosObligatoriosFaltantesError(ServiceError):
    pass


class HorarioNoDisponibleError(ServiceError):
    pass


class ConflictoHorarioError(ServiceError):
    pass


# ============================================================
# Servicio: Solicitante
# ============================================================
class SolicitanteService:
    """
    Servicio para gestión de solicitantes.
    Basado en la lógica de manejo_datos_solicitantes.py
    """

    def __init__(self, repository: SolicitanteRepository):
        self._repo = repository

    def registrar_solicitante(self, dto: SolicitanteDTO) -> SolicitanteDTO:
        """
        Registra un nuevo solicitante.
        Valida datos obligatorios y duplicados.
        """
        # Validar datos obligatorios
        obligatorios = ["cedula", "nombres", "apellidos", "correo", "telefono"]
        faltantes = [campo for campo in obligatorios if not getattr(dto, campo, "").strip()]
        if faltantes:
            raise DatosObligatoriosFaltantesError(f"Faltan datos obligatorios: {', '.join(faltantes)}")

        # Verificar si ya existe
        if self._repo.existe(dto.cedula):
            raise SolicitanteDuplicadoError("La cédula ya está registrada")

        # Crear entidad y guardar
        solicitante = Solicitante(
            cedula=dto.cedula,
            nombres=dto.nombres,
            apellidos=dto.apellidos,
            correo=dto.correo,
            telefono=dto.telefono,
            fechaNacimiento=dto.fecha_nacimiento,
        )

        resultado = self._repo.guardar(solicitante)
        return self._to_dto(resultado)

    def actualizar_contacto(self, cedula: str, correo: str, telefono: str, direccion: str = "") -> SolicitanteDTO:
        """
        Actualiza los datos de contacto de un solicitante.
        """
        # Validar obligatorios
        if not correo.strip() or not telefono.strip():
            raise DatosObligatoriosFaltantesError("Correo y teléfono son obligatorios")

        solicitante = self._repo.obtener_por_cedula(cedula)
        if solicitante is None:
            raise SolicitanteNoEncontradoError(f"No existe solicitante con cédula {cedula}")

        # Actualizar datos (crear nuevo con datos actualizados)
        solicitante_actualizado = Solicitante(
            cedula=solicitante.obtener_cedula(),
            nombres=solicitante._nombres,
            apellidos=solicitante._apellidos,
            correo=correo,
            telefono=telefono,
            fechaNacimiento=solicitante._fecha_nacimiento,
        )

        resultado = self._repo.guardar(solicitante_actualizado)
        return self._to_dto(resultado)

    def obtener_por_cedula(self, cedula: str) -> Optional[SolicitanteDTO]:
        """Obtiene un solicitante por su cédula"""
        solicitante = self._repo.obtener_por_cedula(cedula)
        return self._to_dto(solicitante) if solicitante else None

    def listar_todos(self) -> List[SolicitanteDTO]:
        """Lista todos los solicitantes"""
        return [self._to_dto(s) for s in self._repo.listar_todos()]

    def eliminar(self, cedula: str) -> bool:
        """Elimina un solicitante"""
        return self._repo.eliminar(cedula)

    def existe(self, cedula: str) -> bool:
        """Verifica si existe un solicitante"""
        return self._repo.existe(cedula)

    def _to_dto(self, entity: Solicitante) -> SolicitanteDTO:
        return SolicitanteDTO(
            cedula=entity.obtener_cedula(),
            nombres=entity._nombres,
            apellidos=entity._apellidos,
            correo=entity.obtener_correo(),
            telefono=entity._telefono,
            fecha_nacimiento=entity._fecha_nacimiento,
        )


# ============================================================
# Servicio: Asesor
# ============================================================
class AsesorService:
    """
    Servicio para gestión de asesores.
    """

    def __init__(self, repository: AsesorRepository):
        self._repo = repository

    def registrar_asesor(self, dto: AsesorDTO) -> AsesorDTO:
        """Registra un nuevo asesor"""
        asesor = Asesor(
            nombres=dto.nombres,
            apellidos=dto.apellidos,
            emailAsesor=dto.email,
            rol=RolUsuario[dto.rol],
        )
        resultado = self._repo.guardar(asesor)
        return self._to_dto(resultado)

    def obtener_por_email(self, email: str) -> Optional[AsesorDTO]:
        """Obtiene un asesor por email"""
        asesor = self._repo.obtener_por_email(email)
        return self._to_dto(asesor) if asesor else None

    def listar_todos(self) -> List[AsesorDTO]:
        """Lista todos los asesores"""
        return [self._to_dto(a) for a in self._repo.listar_todos()]

    def listar_activos(self) -> List[AsesorDTO]:
        """Lista asesores activos"""
        return [self._to_dto(a) for a in self._repo.listar_activos()]

    def _to_dto(self, entity: Asesor) -> AsesorDTO:
        return AsesorDTO(
            nombres=entity.nombres,
            apellidos=entity.apellidos,
            email=entity.emailAsesor,
            rol=entity.rol.value,
        )


# ============================================================
# Servicio: SolicitudMigratoria
# ============================================================
class SolicitudMigratoriaService:
    """
    Servicio para gestión de solicitudes migratorias.
    Basado en control_estado_fechas_respectivas_solicitudes.py
    """

    def __init__(self, repository: SolicitudMigratoriaRepository,
                 solicitante_repo: Optional[SolicitanteRepository] = None,
                 asesor_repo: Optional[AsesorRepository] = None):
        self._repo = repository
        self._solicitante_repo = solicitante_repo
        self._asesor_repo = asesor_repo

    def crear_solicitud(self, dto: SolicitudMigratoriaDTO) -> SolicitudMigratoriaDTO:
        """Crea una nueva solicitud migratoria"""
        solicitud = SolicitudMigratoria(
            codigo=dto.codigo,
            tipoServicio=TipoServicio[dto.tipo_servicio] if dto.tipo_servicio else None,
            estadoActual=EstadoSolicitud[dto.estado_actual] if dto.estado_actual else EstadoSolicitud.CREADA,
            fechaCreación=dto.fecha_creacion,
            fechaExpiracion=dto.fecha_expiracion,
        )
        resultado = self._repo.guardar(solicitud)
        return self._to_dto(resultado)

    def obtener_por_codigo(self, codigo: str) -> Optional[SolicitudMigratoriaDTO]:
        """Obtiene una solicitud por código"""
        solicitud = self._repo.obtener_por_codigo(codigo)
        return self._to_dto(solicitud) if solicitud else None

    def cambiar_estado(self, codigo: str, nuevo_estado: str, usuario: str,
                       motivo: str = "", fecha_evento: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Cambia el estado de una solicitud.
        Retorna resultado con estado de la operación.
        """
        solicitud = self._repo.obtener_por_codigo(codigo)
        if solicitud is None:
            raise SolicitudNoEncontradaError(f"No existe solicitud con código {codigo}")

        try:
            solicitud.cambiar_estado(
                nuevo=EstadoSolicitud[nuevo_estado],
                usuario=usuario,
                motivo=motivo,
                fecha_evento=fecha_evento,
            )
            self._repo.guardar(solicitud)
            return {
                "resultado": "aceptado",
                "mensaje": f"Estado cambiado a {nuevo_estado}",
                "solicitud": self._to_dto(solicitud),
            }
        except Exception as e:
            return {
                "resultado": "rechazado",
                "mensaje": str(e),
                "solicitud": self._to_dto(solicitud),
            }

    def asignar_fecha_proceso(self, codigo: str, campo: str, valor_iso: str,
                               usuario: str, fecha_evento: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Asigna una fecha de proceso a la solicitud.
        Campos válidos: fechaRecepcionDocs, fechaEnvioSolicitud, fechaCita
        """
        solicitud = self._repo.obtener_por_codigo(codigo)
        if solicitud is None:
            raise SolicitudNoEncontradaError(f"No existe solicitud con código {codigo}")

        try:
            solicitud.asignar_fecha_proceso(
                campo=campo,
                valor_iso=valor_iso,
                usuario=usuario,
                fecha_evento=fecha_evento,
            )
            self._repo.guardar(solicitud)
            return {
                "resultado": "aceptado",
                "mensaje": f"Fecha {campo} asignada correctamente",
                "solicitud": self._to_dto(solicitud),
            }
        except Exception as e:
            return {
                "resultado": "rechazado",
                "mensaje": str(e),
                "solicitud": self._to_dto(solicitud),
            }

    def obtener_historial_estados(self, codigo: str) -> List[Dict[str, Any]]:
        """Obtiene el historial de estados de una solicitud"""
        solicitud = self._repo.obtener_por_codigo(codigo)
        if solicitud is None:
            raise SolicitudNoEncontradaError(f"No existe solicitud con código {codigo}")
        return solicitud.obtener_historial_estados()

    def obtener_historial_fechas(self, codigo: str) -> List[Dict[str, Any]]:
        """Obtiene el historial de fechas de una solicitud"""
        solicitud = self._repo.obtener_por_codigo(codigo)
        if solicitud is None:
            raise SolicitudNoEncontradaError(f"No existe solicitud con código {codigo}")
        return solicitud.obtener_historial_fechas()

    def obtener_fechas_clave(self, codigo: str) -> Dict[str, Optional[str]]:
        """Obtiene las fechas clave de una solicitud"""
        solicitud = self._repo.obtener_por_codigo(codigo)
        if solicitud is None:
            raise SolicitudNoEncontradaError(f"No existe solicitud con código {codigo}")
        return solicitud.obtener_fechas_clave()

    def listar_todas(self) -> List[SolicitudMigratoriaDTO]:
        """Lista todas las solicitudes"""
        return [self._to_dto(s) for s in self._repo.listar_todas()]

    def listar_por_estado(self, estado: str) -> List[SolicitudMigratoriaDTO]:
        """Lista solicitudes por estado"""
        return [self._to_dto(s) for s in self._repo.listar_por_estado(EstadoSolicitud[estado])]

    def listar_por_solicitante(self, cedula: str) -> List[SolicitudMigratoriaDTO]:
        """Lista solicitudes de un solicitante"""
        return [self._to_dto(s) for s in self._repo.listar_por_solicitante(cedula)]

    def _to_dto(self, entity: SolicitudMigratoria) -> SolicitudMigratoriaDTO:
        return SolicitudMigratoriaDTO(
            codigo=entity.codigo,
            tipo_servicio=entity.tipoServicio.value if entity.tipoServicio else "",
            estado_actual=entity.estadoActual.value,
            fecha_creacion=entity.fechaCreación,
            fecha_expiracion=entity._fecha_expiracion,
            solicitante_cedula=entity._solicitante.obtener_cedula() if entity._solicitante else None,
            asesor_email=entity._asesor.emailAsesor if entity._asesor else None,
            fechas_proceso=entity.obtener_fechas_clave(),
        )


# ============================================================
# Servicio: Documento
# ============================================================
class DocumentoService:
    """
    Servicio para gestión de documentos.
    Basado en recepcion_documentos.py
    """

    def __init__(self, repository: DocumentoRepository,
                 solicitud_repo: Optional[SolicitudMigratoriaRepository] = None):
        self._repo = repository
        self._solicitud_repo = solicitud_repo

    def registrar_documento(self, dto: DocumentoDTO) -> DocumentoDTO:
        """Registra un nuevo documento"""
        documento = Documento(
            id_documento=dto.id_documento,
            tipo=TipoDocumento[dto.tipo],
            estado=EstadoDocumento[dto.estado] if dto.estado else EstadoDocumento.RECIBIDO,
        )
        documento._fecha_expiracion = dto.fecha_expiracion
        documento._version_actual = dto.version_actual
        documento._observacion = dto.observacion

        resultado = self._repo.guardar(documento, dto.solicitud_codigo or "")
        return self._to_dto(resultado)

    def aprobar_documento(self, id_documento: str) -> DocumentoDTO:
        """Aprueba un documento"""
        documento = self._repo.obtener_por_id(id_documento)
        if documento is None:
            raise DocumentoInvalidoError(f"No existe documento con ID {id_documento}")

        documento.marcar_como_aprobado()
        # Nota: Para guardar necesitamos el código de solicitud
        return self._to_dto(documento)

    def rechazar_documento(self, id_documento: str, observacion: str) -> DocumentoDTO:
        """Rechaza un documento con observación"""
        if not observacion.strip():
            raise DocumentoInvalidoError("La observación es obligatoria al rechazar")

        documento = self._repo.obtener_por_id(id_documento)
        if documento is None:
            raise DocumentoInvalidoError(f"No existe documento con ID {id_documento}")

        documento.marcar_como_rechazado(observacion)
        return self._to_dto(documento)

    def verificar_expiracion(self, id_documento: str) -> bool:
        """Verifica si un documento está expirado"""
        documento = self._repo.obtener_por_id(id_documento)
        if documento is None:
            raise DocumentoInvalidoError(f"No existe documento con ID {id_documento}")

        if documento._fecha_expiracion is None:
            return False

        return documento._fecha_expiracion < date.today()

    def obtener_por_id(self, id_documento: str) -> Optional[DocumentoDTO]:
        """Obtiene un documento por ID"""
        documento = self._repo.obtener_por_id(id_documento)
        return self._to_dto(documento) if documento else None

    def listar_por_solicitud(self, solicitud_codigo: str) -> List[DocumentoDTO]:
        """Lista documentos de una solicitud"""
        return [self._to_dto(d) for d in self._repo.listar_por_solicitud(solicitud_codigo)]

    def listar_por_estado(self, estado: str) -> List[DocumentoDTO]:
        """Lista documentos por estado"""
        return [self._to_dto(d) for d in self._repo.listar_por_estado(EstadoDocumento[estado])]

    def _to_dto(self, entity: Documento) -> DocumentoDTO:
        return DocumentoDTO(
            id_documento=entity.obtener_id(),
            tipo=entity.obtener_tipo().value if isinstance(entity.obtener_tipo(), TipoDocumento) else str(entity.obtener_tipo()),
            estado=entity._estado.value,
            fecha_expiracion=entity._fecha_expiracion,
            version_actual=entity._version_actual,
            observacion=entity._observacion or "",
        )


# ============================================================
# Servicio: Tarea
# ============================================================
class TareaService:
    """
    Servicio para gestión de tareas.
    Basado en asignacion_tareas.py
    """

    def __init__(self, repository: TareaRepository,
                 asesor_repo: Optional[AsesorRepository] = None,
                 notificacion_service: Optional["NotificacionService"] = None):
        self._repo = repository
        self._asesor_repo = asesor_repo
        self._notificacion_service = notificacion_service

    def crear_tarea(self, dto: TareaDTO) -> TareaDTO:
        """Crea una nueva tarea"""
        tarea = Tarea(
            idTarea=dto.id_tarea,
            titulo=dto.titulo,
            prioridad=PrioridadTarea[dto.prioridad],
            vencimiento=dto.vencimiento,
            comentario=dto.comentario,
            estado=EstadoTarea[dto.estado] if dto.estado else EstadoTarea.PENDIENTE,
        )
        resultado = self._repo.guardar(tarea)
        return self._to_dto(resultado)

    def asignar_a_asesor(self, id_tarea: str, email_asesor: str,
                          vencimiento: Optional[datetime] = None,
                          enviar_notificacion: bool = True) -> TareaDTO:
        """
        Asigna una tarea a un asesor.
        Opcionalmente establece fecha de vencimiento y envía notificación.
        """
        tarea = self._repo.obtener_por_id(id_tarea)
        if tarea is None:
            raise TareaNoEncontradaError(f"No existe la tarea {id_tarea}")

        if self._asesor_repo is None:
            raise ServiceError("Repositorio de asesores no configurado")

        asesor = self._asesor_repo.obtener_por_email(email_asesor)
        if asesor is None:
            raise AsesorNoEncontradoError(f"No existe asesor con email {email_asesor}")

        # Asignar tarea
        tarea.asignar_a_asesor(asesor)

        # Establecer vencimiento si se proporciona
        if vencimiento:
            tarea.establecer_vencimiento(vencimiento)

        resultado = self._repo.guardar(tarea)

        # Enviar notificación si está configurado
        if enviar_notificacion and self._notificacion_service:
            self._notificacion_service.crear_notificacion_asignacion(
                destinatario=email_asesor,
                tarea_titulo=tarea.titulo,
                tarea_prioridad=tarea.prioridad.value,
            )

        return self._to_dto(resultado)

    def editar_tarea(
        self,
        id_tarea: str,
        *,
        titulo: Optional[str] = None,
        prioridad: Optional[str] = None,
        estado: Optional[str] = None,
        vencimiento: Optional[datetime] = None,
        comentario: Optional[str] = None,
    ) -> TareaDTO:
        """
        Edita una tarea existente (campos opcionales).
        Nota: No reasigna asesor; para eso usar `asignar_a_asesor`.
        """
        tarea = self._repo.obtener_por_id(id_tarea)
        if tarea is None:
            raise TareaNoEncontradaError(f"No existe la tarea {id_tarea}")

        if titulo is not None:
            tarea.titulo = titulo

        if prioridad is not None:
            tarea.actualizar_prioridad(PrioridadTarea[prioridad])

        if estado is not None:
            tarea.cambiar_estado(EstadoTarea[estado])

        if vencimiento is not None:
            tarea.establecer_vencimiento(vencimiento)

        if comentario is not None:
            tarea.comentario = comentario

        resultado = self._repo.guardar(tarea)
        return self._to_dto(resultado)

    def cambiar_estado(self, id_tarea: str, nuevo_estado: str) -> TareaDTO:
        """Cambia el estado de una tarea"""
        tarea = self._repo.obtener_por_id(id_tarea)
        if tarea is None:
            raise TareaNoEncontradaError(f"No existe la tarea {id_tarea}")

        tarea.cambiar_estado(EstadoTarea[nuevo_estado])
        resultado = self._repo.guardar(tarea)
        return self._to_dto(resultado)

    def actualizar_prioridad(self, id_tarea: str, nueva_prioridad: str) -> TareaDTO:
        """Actualiza la prioridad de una tarea"""
        tarea = self._repo.obtener_por_id(id_tarea)
        if tarea is None:
            raise TareaNoEncontradaError(f"No existe la tarea {id_tarea}")

        tarea.actualizar_prioridad(PrioridadTarea[nueva_prioridad])
        resultado = self._repo.guardar(tarea)
        return self._to_dto(resultado)

    def obtener_por_id(self, id_tarea: str) -> Optional[TareaDTO]:
        """Obtiene una tarea por ID"""
        tarea = self._repo.obtener_por_id(id_tarea)
        return self._to_dto(tarea) if tarea else None

    def listar_todas(self) -> List[TareaDTO]:
        """Lista todas las tareas"""
        return [self._to_dto(t) for t in self._repo.listar_todas()]

    def listar_por_asesor(self, email_asesor: str) -> List[TareaDTO]:
        """Lista tareas asignadas a un asesor"""
        return [self._to_dto(t) for t in self._repo.listar_por_asesor(email_asesor)]

    def listar_por_estado(self, estado: str) -> List[TareaDTO]:
        """Lista tareas por estado"""
        return [self._to_dto(t) for t in self._repo.listar_por_estado(EstadoTarea[estado])]

    def listar_vencidas(self) -> List[TareaDTO]:
        """Lista tareas vencidas"""
        return [self._to_dto(t) for t in self._repo.listar_vencidas()]

    def listar_por_vencer(self, horas: int = 24) -> List[TareaDTO]:
        """Lista tareas próximas a vencer"""
        return [self._to_dto(t) for t in self._repo.listar_por_vencer(horas)]

    def enviar_recordatorios_vencimiento(self) -> int:
        """
        Envía recordatorios para tareas próximas a vencer.
        Retorna cantidad de notificaciones enviadas.
        """
        if self._notificacion_service is None:
            return 0

        tareas_por_vencer = self._repo.listar_por_vencer(24)
        count = 0

        for tarea in tareas_por_vencer:
            if tarea.asignadaA:
                self._notificacion_service.crear_recordatorio_vencimiento(
                    destinatario=tarea.asignadaA.emailAsesor,
                    tarea_titulo=tarea.titulo,
                    fecha_vencimiento=tarea.vencimiento,
                )
                count += 1

        return count

    def _to_dto(self, entity: Tarea) -> TareaDTO:
        return TareaDTO(
            id_tarea=entity.idTarea,
            titulo=entity.titulo,
            prioridad=entity.prioridad.value,
            estado=entity.estado.value,
            vencimiento=entity.vencimiento,
            comentario=entity.comentario,
            asesor_email=entity.asignadaA.emailAsesor if entity.asignadaA else None,
        )


# ============================================================
# Servicio: Cita
# ============================================================
class CitaService:
    """
    Servicio para gestión de citas.
    Basado en reservacion_citas_solicitantes.py
    """

    def __init__(self, repository: CitaRepository,
                 solicitud_repo: Optional[SolicitudMigratoriaRepository] = None,
                 notificacion_service: Optional["NotificacionService"] = None):
        self._repo = repository
        self._solicitud_repo = solicitud_repo
        self._notificacion_service = notificacion_service

    def agendar_cita(self, dto: CitaDTO) -> CitaDTO:
        """
        Agenda una nueva cita.
        Verifica disponibilidad de horario.
        """
        if dto.inicio is None or dto.fin is None:
            raise CitaInvalidaError("Debe especificar inicio y fin de la cita")

        # Verificar disponibilidad
        if not self._repo.verificar_disponibilidad(dto.inicio, dto.fin):
            raise HorarioNoDisponibleError("El horario no está disponible")

        cita = Cita(
            idCita=dto.id_cita,
            solicitudCodigo=dto.solicitud_codigo,
            observacion=dto.observacion,
            rango=RangoFechaHora(inicio=dto.inicio, fin=dto.fin),
            tipo=TipoCita[dto.tipo],
            estado=EstadoCita.PROGRAMADA,
        )

        resultado = self._repo.guardar(cita)
        return self._to_dto(resultado)

    def reprogramar_cita(self, id_cita: str, nuevo_inicio: datetime, nuevo_fin: datetime,
                          motivo: str = "") -> CitaDTO:
        """
        Reprograma una cita existente.
        Verifica disponibilidad del nuevo horario.
        """
        cita = self._repo.obtener_por_id(id_cita)
        if cita is None:
            raise CitaInvalidaError(f"No existe cita con ID {id_cita}")

        # Verificar que la cita se pueda reprogramar
        if cita.estado in [EstadoCita.CANCELADA, EstadoCita.COMPLETADA]:
            raise CitaInvalidaError(f"No se puede reprogramar una cita {cita.estado.value}")

        # Verificar disponibilidad (excluyendo la cita actual)
        if not self._verificar_disponibilidad_excluyendo(nuevo_inicio, nuevo_fin, id_cita):
            raise HorarioNoDisponibleError("El nuevo horario no está disponible")

        # Crear nueva cita reprogramada
        cita_reprogramada = Cita(
            idCita=cita.idCita,
            solicitudCodigo=cita.solicitudCodigo,
            observacion=f"{cita.observacion}\nReprogramada: {motivo}".strip(),
            rango=RangoFechaHora(inicio=nuevo_inicio, fin=nuevo_fin),
            tipo=cita.tipo,
            estado=EstadoCita.REPROGRAMADA,
        )

        resultado = self._repo.guardar(cita_reprogramada)
        return self._to_dto(resultado)

    def cancelar_cita(self, id_cita: str, motivo: str = "") -> CitaDTO:
        """Cancela una cita"""
        cita = self._repo.obtener_por_id(id_cita)
        if cita is None:
            raise CitaInvalidaError(f"No existe cita con ID {id_cita}")

        cita_cancelada = Cita(
            idCita=cita.idCita,
            solicitudCodigo=cita.solicitudCodigo,
            observacion=f"{cita.observacion}\nCancelada: {motivo}".strip(),
            rango=cita.rango,
            tipo=cita.tipo,
            estado=EstadoCita.CANCELADA,
        )

        resultado = self._repo.guardar(cita_cancelada)
        return self._to_dto(resultado)

    def completar_cita(self, id_cita: str) -> CitaDTO:
        """Marca una cita como completada"""
        cita = self._repo.obtener_por_id(id_cita)
        if cita is None:
            raise CitaInvalidaError(f"No existe cita con ID {id_cita}")

        cita_completada = Cita(
            idCita=cita.idCita,
            solicitudCodigo=cita.solicitudCodigo,
            observacion=cita.observacion,
            rango=cita.rango,
            tipo=cita.tipo,
            estado=EstadoCita.COMPLETADA,
        )

        resultado = self._repo.guardar(cita_completada)
        return self._to_dto(resultado)

    def marcar_no_asistio(self, id_cita: str) -> CitaDTO:
        """Marca que el solicitante no asistió a la cita"""
        cita = self._repo.obtener_por_id(id_cita)
        if cita is None:
            raise CitaInvalidaError(f"No existe cita con ID {id_cita}")

        cita_no_asistio = Cita(
            idCita=cita.idCita,
            solicitudCodigo=cita.solicitudCodigo,
            observacion=cita.observacion,
            rango=cita.rango,
            tipo=cita.tipo,
            estado=EstadoCita.NO_ASISTIO,
        )

        resultado = self._repo.guardar(cita_no_asistio)
        return self._to_dto(resultado)

    def verificar_disponibilidad(self, inicio: datetime, fin: datetime) -> bool:
        """Verifica si hay disponibilidad en el horario"""
        return self._repo.verificar_disponibilidad(inicio, fin)

    def obtener_por_id(self, id_cita: str) -> Optional[CitaDTO]:
        """Obtiene una cita por ID"""
        cita = self._repo.obtener_por_id(id_cita)
        return self._to_dto(cita) if cita else None

    def listar_por_solicitud(self, solicitud_codigo: str) -> List[CitaDTO]:
        """Lista citas de una solicitud"""
        return [self._to_dto(c) for c in self._repo.listar_por_solicitud(solicitud_codigo)]

    def listar_por_rango_fecha(self, inicio: datetime, fin: datetime) -> List[CitaDTO]:
        """Lista citas en un rango de fechas"""
        return [self._to_dto(c) for c in self._repo.listar_por_rango_fecha(inicio, fin)]

    def obtener_agenda(self, fecha: date) -> List[CitaDTO]:
        """Obtiene la agenda del día"""
        inicio = datetime.combine(fecha, datetime.min.time())
        fin = datetime.combine(fecha, datetime.max.time())
        return self.listar_por_rango_fecha(inicio, fin)

    def _verificar_disponibilidad_excluyendo(self, inicio: datetime, fin: datetime,
                                              excluir_cita_id: str) -> bool:
        """Verifica disponibilidad excluyendo una cita específica"""
        citas = self._repo.listar_por_rango_fecha(inicio, fin)
        for cita in citas:
            if cita.idCita != excluir_cita_id and cita.estado not in [EstadoCita.CANCELADA, EstadoCita.COMPLETADA]:
                # Verificar solapamiento
                if cita.rango.inicio < fin and cita.rango.fin > inicio:
                    return False
        return True

    def _to_dto(self, entity: Cita) -> CitaDTO:
        return CitaDTO(
            id_cita=entity.idCita,
            solicitud_codigo=entity.solicitudCodigo,
            tipo=entity.tipo.value,
            estado=entity.estado.value,
            inicio=entity.rango.inicio,
            fin=entity.rango.fin,
            observacion=entity.observacion,
        )


# ============================================================
# Servicio: Notificacion
# ============================================================
class NotificacionService:
    """
    Servicio para gestión de notificaciones.
    """

    def __init__(self, repository: NotificacionRepository):
        self._repo = repository
        self._contador = 0

    def _generar_id(self) -> str:
        """Genera un ID único para la notificación"""
        self._contador += 1
        return f"NOTIF-{self._contador:03d}"

    def crear_notificacion(self, destinatario: str, tipo: str, mensaje: str) -> NotificacionDTO:
        """Crea una nueva notificación"""
        notificacion = Notificacion(
            id_notificacion=self._generar_id(),
            destinatario=destinatario,
            tipo=TipoNotificacion[tipo],
            mensaje=mensaje,
        )
        resultado = self._repo.guardar(notificacion)
        return self._to_dto(resultado)

    def crear_notificacion_asignacion(self, destinatario: str, tarea_titulo: str,
                                       tarea_prioridad: str) -> NotificacionDTO:
        """Crea notificación de asignación de tarea"""
        mensaje = f"Se te ha asignado la tarea '{tarea_titulo}' con prioridad {tarea_prioridad}"
        return self.crear_notificacion(destinatario, "ASIGNACION_TAREA", mensaje)

    def crear_recordatorio_vencimiento(self, destinatario: str, tarea_titulo: str,
                                        fecha_vencimiento: Optional[datetime]) -> NotificacionDTO:
        """Crea recordatorio de vencimiento de tarea"""
        fecha_str = fecha_vencimiento.strftime("%Y-%m-%d %H:%M") if fecha_vencimiento else "próximamente"
        mensaje = f"Recordatorio: La tarea '{tarea_titulo}' vence el {fecha_str}"
        return self.crear_notificacion(destinatario, "RECORDATORIO", mensaje)

    def crear_recordatorio_cita(self, destinatario: str, fecha_cita: datetime,
                                 tipo_cita: str) -> NotificacionDTO:
        """Crea recordatorio de cita próxima"""
        mensaje = f"Recordatorio: Tiene una cita de {tipo_cita} programada para {fecha_cita.strftime('%Y-%m-%d %H:%M')}"
        return self.crear_notificacion(destinatario, "CITA_PROXIMA", mensaje)

    def marcar_como_leida(self, id_notificacion: str) -> bool:
        """Marca una notificación como leída"""
        return self._repo.marcar_como_leida(id_notificacion)

    def obtener_por_id(self, id_notificacion: str) -> Optional[NotificacionDTO]:
        """Obtiene una notificación por ID"""
        notificacion = self._repo.obtener_por_id(id_notificacion)
        return self._to_dto(notificacion) if notificacion else None

    def listar_por_destinatario(self, destinatario: str) -> List[NotificacionDTO]:
        """Lista notificaciones de un destinatario"""
        return [self._to_dto(n) for n in self._repo.listar_por_destinatario(destinatario)]

    def listar_no_leidas(self, destinatario: str) -> List[NotificacionDTO]:
        """Lista notificaciones no leídas"""
        return [self._to_dto(n) for n in self._repo.listar_no_leidas(destinatario)]

    def _to_dto(self, entity: Notificacion) -> NotificacionDTO:
        return NotificacionDTO(
            id_notificacion=entity._id,
            destinatario=entity.obtener_destinatario(),
            tipo=entity.obtener_tipo().value,
            mensaje=entity.obtener_mensaje(),
            creada_en=entity._creada_en,
            leida=entity.esta_leida(),
        )


# ============================================================
# Servicio: ReporteTareas
# ============================================================
class ReporteTareasService:
    """
    Servicio para generación de reportes y estadísticas de tareas.
    Basado en generacion_reporte_estadisticas_tareas.py
    """

    def __init__(self, tarea_repo: TareaRepository,
                 asesor_repo: Optional[AsesorRepository] = None):
        self._tarea_repo = tarea_repo
        self._asesor_repo = asesor_repo
        self._contador_reportes = 0

    def generar_reporte(self, filtro: FiltroReporteTareasDTO,
                        momento_actual: Optional[datetime] = None) -> ReporteTareasDTO:
        """
        Genera un reporte de tareas según el filtro especificado.
        """
        momento = momento_actual or datetime.now()

        # Obtener todas las tareas
        todas_las_tareas = self._tarea_repo.listar_todas()

        # Filtrar por período (usando vencimiento como referencia)
        tareas_filtradas = [
            t for t in todas_las_tareas
            if t.vencimiento and filtro.desde <= t.vencimiento <= filtro.hasta
        ]

        # Filtrar por asesor si se especifica
        if filtro.asesor_email:
            tareas_filtradas = [
                t for t in tareas_filtradas
                if t.asignadaA and t.asignadaA.emailAsesor == filtro.asesor_email
            ]

        # Calcular estadísticas
        estadisticas = self._calcular_estadisticas(tareas_filtradas, momento)

        # Generar ID de reporte
        self._contador_reportes += 1
        id_reporte = f"REP-{self._contador_reportes:03d}"

        return ReporteTareasDTO(
            id_reporte=id_reporte,
            creado_en=momento,
            filtro=filtro,
            estadisticas=estadisticas,
        )

    def generar_resumen_global(
        self,
        *,
        momento_actual: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Genera un resumen listo para renderizar en templates (sin filtros por fecha).

        Retorna un dict con la forma esperada por `templates/tareas/reportes.html`:
        - total, completadas, vencidas
        - por_estado, por_prioridad
        - por_asesor: {email: {nombre, total, completadas, pendientes}}
        """
        momento = momento_actual or datetime.now()
        tareas = self._tarea_repo.listar_todas()
        estadisticas = self._calcular_estadisticas(tareas, momento)

        completadas = estadisticas.por_estado.get(EstadoTarea.COMPLETADA.value, 0)
        vencidas = estadisticas.vencidas_total

        por_asesor: Dict[str, Dict[str, Any]] = {}
        for t in tareas:
            if not t.asignadaA:
                continue
            email = t.asignadaA.emailAsesor
            entry = por_asesor.setdefault(
                email,
                {"nombre": email, "total": 0, "completadas": 0, "pendientes": 0},
            )
            entry["total"] += 1
            if t.estado == EstadoTarea.COMPLETADA:
                entry["completadas"] += 1
            elif t.estado in (EstadoTarea.PENDIENTE, EstadoTarea.EN_PROGRESO):
                entry["pendientes"] += 1

        # Si tenemos repositorio de asesores, reemplazar nombre por nombre completo
        if self._asesor_repo is not None:
            for email, datos in por_asesor.items():
                asesor = self._asesor_repo.obtener_por_email(email)
                if asesor:
                    datos["nombre"] = asesor.obtener_nombre_completo()

        return {
            "total": estadisticas.total_tareas,
            "completadas": completadas,
            "vencidas": vencidas,
            "por_estado": estadisticas.por_estado,
            "por_prioridad": estadisticas.por_prioridad,
            "por_asesor": por_asesor,
        }

    def _calcular_estadisticas(self, tareas: List[Tarea],
                                momento: datetime) -> EstadisticasTareasDTO:
        """Calcula estadísticas a partir de lista de tareas"""
        # Normalizar comparaciones de datetime (naive vs aware) para evitar TypeError en Django
        try:
            from django.utils import timezone as dj_timezone  # type: ignore
        except Exception:  # pragma: no cover
            dj_timezone = None

        # Conteo por estado
        por_estado = {e.value: 0 for e in EstadoTarea}
        for t in tareas:
            por_estado[t.estado.value] += 1

        # Conteo por prioridad
        por_prioridad = {p.value: 0 for p in PrioridadTarea}
        for t in tareas:
            por_prioridad[t.prioridad.value] += 1

        # Vencidas (no completadas/canceladas con vencimiento pasado)
        vencidas_por_asesor: Dict[str, int] = {}
        vencidas_total = 0
        for t in tareas:
            if t.estado in [EstadoTarea.PENDIENTE, EstadoTarea.EN_PROGRESO]:
                if t.vencimiento:
                    venc = t.vencimiento
                    mom = momento
                    if dj_timezone is not None:
                        tz = dj_timezone.get_current_timezone()
                        if dj_timezone.is_aware(venc) and dj_timezone.is_naive(mom):
                            mom = dj_timezone.make_aware(mom, tz)
                        elif dj_timezone.is_naive(venc) and dj_timezone.is_aware(mom):
                            venc = dj_timezone.make_aware(venc, tz)

                    if venc < mom:
                        vencidas_total += 1
                        if t.asignadaA:
                            email = t.asignadaA.emailAsesor
                            vencidas_por_asesor[email] = vencidas_por_asesor.get(email, 0) + 1

        # Completadas por asesor
        completadas_por_asesor: Dict[str, int] = {}
        for t in tareas:
            if t.estado == EstadoTarea.COMPLETADA and t.asignadaA:
                email = t.asignadaA.emailAsesor
                completadas_por_asesor[email] = completadas_por_asesor.get(email, 0) + 1

        return EstadisticasTareasDTO(
            total_tareas=len(tareas),
            por_estado=por_estado,
            por_prioridad=por_prioridad,
            vencidas_total=vencidas_total,
            vencidas_por_asesor=vencidas_por_asesor,
            completadas_por_asesor=completadas_por_asesor,
        )

    def obtener_ranking_completadas(self, filtro: FiltroReporteTareasDTO) -> List[Tuple[str, int]]:
        """
        Obtiene ranking de asesores por tareas completadas.
        Retorna lista de tuplas (email, cantidad) ordenada descendentemente.
        """
        reporte = self.generar_reporte(filtro)
        ranking = sorted(
            reporte.estadisticas.completadas_por_asesor.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranking

    def obtener_tareas_vencidas_por_asesor(self, email_asesor: str,
                                            momento: Optional[datetime] = None) -> List[TareaDTO]:
        """Obtiene las tareas vencidas de un asesor específico"""
        momento = momento or datetime.now()
        tareas = self._tarea_repo.listar_por_asesor(email_asesor)

        vencidas = [
            t for t in tareas
            if t.estado in [EstadoTarea.PENDIENTE, EstadoTarea.EN_PROGRESO]
            and t.vencimiento and t.vencimiento < momento
        ]

        return [self._tarea_to_dto(t) for t in vencidas]

    def exportar_reporte(self, reporte: ReporteTareasDTO, formato: str = "JSON") -> Dict[str, Any]:
        """
        Exporta el reporte en el formato especificado.
        Formatos soportados: JSON, CSV (representado como dict)
        """
        datos = {
            "id_reporte": reporte.id_reporte,
            "creado_en": reporte.creado_en.isoformat(),
            "filtro": {
                "desde": reporte.filtro.desde.isoformat(),
                "hasta": reporte.filtro.hasta.isoformat(),
                "asesor_email": reporte.filtro.asesor_email,
            },
            "estadisticas": {
                "total_tareas": reporte.estadisticas.total_tareas,
                "por_estado": reporte.estadisticas.por_estado,
                "por_prioridad": reporte.estadisticas.por_prioridad,
                "vencidas_total": reporte.estadisticas.vencidas_total,
                "vencidas_por_asesor": reporte.estadisticas.vencidas_por_asesor,
                "completadas_por_asesor": reporte.estadisticas.completadas_por_asesor,
            },
            "formato": formato,
        }
        return datos

    def _tarea_to_dto(self, entity: Tarea) -> TareaDTO:
        return TareaDTO(
            id_tarea=entity.idTarea,
            titulo=entity.titulo,
            prioridad=entity.prioridad.value,
            estado=entity.estado.value,
            vencimiento=entity.vencimiento,
            comentario=entity.comentario,
            asesor_email=entity.asignadaA.emailAsesor if entity.asignadaA else None,
        )
