"""
Repositorios concretos de infraestructura.
Implementan los contratos definidos en domain.repositories usando Django ORM.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List

from django.db.models import Q

from SGPM.domain.repositories import (
    SolicitanteRepository,
    AsesorRepository,
    SolicitudMigratoriaRepository,
    DocumentoRepository,
    TareaRepository,
    CitaRepository,
    NotificacionRepository,
)
from SGPM.domain.entities import (
    Solicitante as SolicitanteEntity,
    Asesor as AsesorEntity,
    SolicitudMigratoria as SolicitudMigratoriaEntity,
    Documento as DocumentoEntity,
    Tarea as TareaEntity,
    Cita as CitaEntity,
    Notificacion as NotificacionEntity,
)
from SGPM.domain.enums import (
    RolUsuario,
    EstadoSolicitud,
    EstadoDocumento,
    EstadoTarea,
    EstadoCita,
    TipoDocumento,
    TipoCita,
    PrioridadTarea,
)
from SGPM.domain.value_objects import RangoFechaHora
from .models import (
    Solicitante as SolicitanteModel,
    Asesor as AsesorModel,
    SolicitudMigratoria as SolicitudMigratoriaModel,
    Documento as DocumentoModel,
    Tarea as TareaModel,
    Cita as CitaModel,
    Notificacion as NotificacionModel,
)


# ========================================
# Repositorio: DjangoSolicitanteRepository
# ========================================
class DjangoSolicitanteRepository(SolicitanteRepository):
    """Implementación Django ORM del repositorio de Solicitante"""

    def _to_entity(self, model: SolicitanteModel) -> SolicitanteEntity:
        """Convierte un modelo Django a entidad de dominio"""
        return SolicitanteEntity(
            cedula=model.cedula,
            nombres=model.nombres,
            apellidos=model.apellidos,
            correo=model.correo,
            telefono=model.telefono,
            fechaNacimiento=model.fecha_nacimiento,
        )

    def _to_model(self, entity: SolicitanteEntity) -> SolicitanteModel:
        """Convierte una entidad de dominio a modelo Django"""
        model, _ = SolicitanteModel.objects.get_or_create(
            cedula=entity.obtener_cedula(),
            defaults={
                'nombres': entity._nombres,
                'apellidos': entity._apellidos,
                'correo': entity.obtener_correo(),
                'telefono': entity._telefono,
                'fecha_nacimiento': entity._fecha_nacimiento,
            }
        )
        return model

    def guardar(self, solicitante: SolicitanteEntity) -> SolicitanteEntity:
        model, created = SolicitanteModel.objects.update_or_create(
            cedula=solicitante.obtener_cedula(),
            defaults={
                'nombres': solicitante._nombres,
                'apellidos': solicitante._apellidos,
                'correo': solicitante.obtener_correo(),
                'telefono': solicitante._telefono,
                'fecha_nacimiento': solicitante._fecha_nacimiento,
            }
        )
        return self._to_entity(model)

    def obtener_por_cedula(self, cedula: str) -> Optional[SolicitanteEntity]:
        try:
            model = SolicitanteModel.objects.get(cedula=cedula)
            return self._to_entity(model)
        except SolicitanteModel.DoesNotExist:
            return None

    def obtener_por_correo(self, correo: str) -> Optional[SolicitanteEntity]:
        try:
            model = SolicitanteModel.objects.get(correo=correo)
            return self._to_entity(model)
        except SolicitanteModel.DoesNotExist:
            return None

    def listar_todos(self) -> List[SolicitanteEntity]:
        return [self._to_entity(m) for m in SolicitanteModel.objects.all()]

    def eliminar(self, cedula: str) -> bool:
        deleted, _ = SolicitanteModel.objects.filter(cedula=cedula).delete()
        return deleted > 0

    def existe(self, cedula: str) -> bool:
        return SolicitanteModel.objects.filter(cedula=cedula).exists()


# ========================================
# Repositorio: DjangoAsesorRepository
# ========================================
class DjangoAsesorRepository(AsesorRepository):
    """Implementación Django ORM del repositorio de Asesor"""

    def _to_entity(self, model: AsesorModel) -> AsesorEntity:
        return AsesorEntity(
            nombres=model.nombres,
            apellidos=model.apellidos,
            emailAsesor=model.email_asesor,
            rol=RolUsuario(model.rol),
        )

    def guardar(self, asesor: AsesorEntity) -> AsesorEntity:
        model, _ = AsesorModel.objects.update_or_create(
            email_asesor=asesor.emailAsesor,
            defaults={
                'nombres': asesor.nombres,
                'apellidos': asesor.apellidos,
                'rol': asesor.rol.value,
            }
        )
        return self._to_entity(model)

    def obtener_por_email(self, email: str) -> Optional[AsesorEntity]:
        try:
            model = AsesorModel.objects.get(email_asesor=email)
            return self._to_entity(model)
        except AsesorModel.DoesNotExist:
            return None

    def listar_todos(self) -> List[AsesorEntity]:
        return [self._to_entity(m) for m in AsesorModel.objects.all()]

    def listar_activos(self) -> List[AsesorEntity]:
        return [self._to_entity(m) for m in AsesorModel.objects.filter(activo=True)]

    def eliminar(self, email: str) -> bool:
        deleted, _ = AsesorModel.objects.filter(email_asesor=email).delete()
        return deleted > 0

    def existe(self, email: str) -> bool:
        return AsesorModel.objects.filter(email_asesor=email).exists()


# ========================================
# Repositorio: DjangoSolicitudMigratoriaRepository
# ========================================
class DjangoSolicitudMigratoriaRepository(SolicitudMigratoriaRepository):
    """Implementación Django ORM del repositorio de SolicitudMigratoria"""

    def _to_entity(self, model: SolicitudMigratoriaModel) -> SolicitudMigratoriaEntity:
        # Convertir solicitante si existe
        solicitante = None
        if model.solicitante:
            solicitante = SolicitanteEntity(
                cedula=model.solicitante.cedula,
                nombres=model.solicitante.nombres,
                apellidos=model.solicitante.apellidos,
                correo=model.solicitante.correo,
                telefono=model.solicitante.telefono,
                fechaNacimiento=model.solicitante.fecha_nacimiento,
            )

        # Convertir asesor si existe
        asesor = None
        if model.asesor:
            asesor = AsesorEntity(
                nombres=model.asesor.nombres,
                apellidos=model.asesor.apellidos,
                emailAsesor=model.asesor.email_asesor,
                rol=RolUsuario(model.asesor.rol),
            )

        from SGPM.domain.enums import TipoServicio
        tipo_servicio = TipoServicio(model.tipo_servicio) if model.tipo_servicio else None

        return SolicitudMigratoriaEntity(
            codigo=model.codigo,
            tipoServicio=tipo_servicio,
            estadoActual=EstadoSolicitud(model.estado_actual),
            fechaCreación=model.fecha_creacion,
            fechaExpiracion=model.fecha_expiracion,
            solicitante=solicitante,
            asesor=asesor,
        )

    def guardar(self, solicitud: SolicitudMigratoriaEntity) -> SolicitudMigratoriaEntity:
        # Obtener o crear solicitante si existe
        solicitante_model = None
        if solicitud._solicitante:
            solicitante_model, _ = SolicitanteModel.objects.get_or_create(
                cedula=solicitud._solicitante.obtener_cedula(),
                defaults={
                    'nombres': solicitud._solicitante._nombres,
                    'apellidos': solicitud._solicitante._apellidos,
                    'correo': solicitud._solicitante.obtener_correo(),
                    'telefono': solicitud._solicitante._telefono,
                }
            )

        # Obtener asesor si existe
        asesor_model = None
        if solicitud._asesor:
            asesor_model = AsesorModel.objects.filter(
                email_asesor=solicitud._asesor.emailAsesor
            ).first()

        model, _ = SolicitudMigratoriaModel.objects.update_or_create(
            codigo=solicitud.codigo,
            defaults={
                'tipo_servicio': solicitud.tipoServicio.value if solicitud.tipoServicio else None,
                'estado_actual': solicitud.estadoActual.value,
                'fecha_expiracion': solicitud._fecha_expiracion,
                'solicitante': solicitante_model,
                'asesor': asesor_model,
                'fecha_recepcion_docs': solicitud.obtener_fecha_proceso('fechaRecepcionDocs'),
                'fecha_envio_solicitud': solicitud.obtener_fecha_proceso('fechaEnvioSolicitud'),
                'fecha_cita': solicitud.obtener_fecha_proceso('fechaCita'),
            }
        )
        return self._to_entity(model)

    def obtener_por_codigo(self, codigo: str) -> Optional[SolicitudMigratoriaEntity]:
        try:
            model = SolicitudMigratoriaModel.objects.select_related(
                'solicitante', 'asesor'
            ).get(codigo=codigo)
            return self._to_entity(model)
        except SolicitudMigratoriaModel.DoesNotExist:
            return None

    def listar_todas(self) -> List[SolicitudMigratoriaEntity]:
        return [
            self._to_entity(m) for m in
            SolicitudMigratoriaModel.objects.select_related('solicitante', 'asesor').all()
        ]

    def listar_por_estado(self, estado: EstadoSolicitud) -> List[SolicitudMigratoriaEntity]:
        return [
            self._to_entity(m) for m in
            SolicitudMigratoriaModel.objects.filter(estado_actual=estado.value)
        ]

    def listar_por_solicitante(self, cedula: str) -> List[SolicitudMigratoriaEntity]:
        return [
            self._to_entity(m) for m in
            SolicitudMigratoriaModel.objects.filter(solicitante__cedula=cedula)
        ]

    def listar_por_asesor(self, email_asesor: str) -> List[SolicitudMigratoriaEntity]:
        return [
            self._to_entity(m) for m in
            SolicitudMigratoriaModel.objects.filter(asesor__email_asesor=email_asesor)
        ]

    def eliminar(self, codigo: str) -> bool:
        deleted, _ = SolicitudMigratoriaModel.objects.filter(codigo=codigo).delete()
        return deleted > 0

    def existe(self, codigo: str) -> bool:
        return SolicitudMigratoriaModel.objects.filter(codigo=codigo).exists()


# ========================================
# Repositorio: DjangoDocumentoRepository
# ========================================
class DjangoDocumentoRepository(DocumentoRepository):
    """Implementación Django ORM del repositorio de Documento"""

    def _to_entity(self, model: DocumentoModel) -> DocumentoEntity:
        entity = DocumentoEntity(
            id_documento=model.id_documento,
            tipo=TipoDocumento(model.tipo),
            estado=EstadoDocumento(model.estado),
        )
        entity._fecha_expiracion = model.fecha_expiracion
        entity._version_actual = model.version_actual
        entity._observacion = model.observacion
        return entity

    def guardar(self, documento: DocumentoEntity, solicitud_codigo: str) -> DocumentoEntity:
        solicitud = SolicitudMigratoriaModel.objects.get(codigo=solicitud_codigo)
        model, _ = DocumentoModel.objects.update_or_create(
            id_documento=documento.obtener_id(),
            defaults={
                'solicitud': solicitud,
                'tipo': documento.obtener_tipo().value if isinstance(documento.obtener_tipo(), TipoDocumento) else documento.obtener_tipo(),
                'estado': documento._estado.value,
                'fecha_expiracion': documento._fecha_expiracion,
                'version_actual': documento._version_actual,
                'observacion': documento._observacion,
            }
        )
        return self._to_entity(model)

    def obtener_por_id(self, id_documento: str) -> Optional[DocumentoEntity]:
        try:
            model = DocumentoModel.objects.get(id_documento=id_documento)
            return self._to_entity(model)
        except DocumentoModel.DoesNotExist:
            return None

    def listar_por_solicitud(self, solicitud_codigo: str) -> List[DocumentoEntity]:
        return [
            self._to_entity(m) for m in
            DocumentoModel.objects.filter(solicitud__codigo=solicitud_codigo)
        ]

    def listar_por_estado(self, estado: EstadoDocumento) -> List[DocumentoEntity]:
        return [
            self._to_entity(m) for m in
            DocumentoModel.objects.filter(estado=estado.value)
        ]

    def listar_por_tipo(self, tipo: TipoDocumento) -> List[DocumentoEntity]:
        return [
            self._to_entity(m) for m in
            DocumentoModel.objects.filter(tipo=tipo.value)
        ]

    def eliminar(self, id_documento: str) -> bool:
        deleted, _ = DocumentoModel.objects.filter(id_documento=id_documento).delete()
        return deleted > 0

    def existe(self, id_documento: str) -> bool:
        return DocumentoModel.objects.filter(id_documento=id_documento).exists()


# ========================================
# Repositorio: DjangoTareaRepository
# ========================================
class DjangoTareaRepository(TareaRepository):
    """Implementación Django ORM del repositorio de Tarea"""

    def _to_entity(self, model: TareaModel) -> TareaEntity:
        asesor = None
        if model.asignada_a:
            asesor = AsesorEntity(
                nombres=model.asignada_a.nombres,
                apellidos=model.asignada_a.apellidos,
                emailAsesor=model.asignada_a.email_asesor,
                rol=RolUsuario(model.asignada_a.rol),
            )

        return TareaEntity(
            idTarea=model.id_tarea,
            titulo=model.titulo,
            prioridad=PrioridadTarea(model.prioridad),
            vencimiento=model.vencimiento,
            comentario=model.comentario,
            estado=EstadoTarea(model.estado),
            asignadaA=asesor,
        )

    def guardar(self, tarea: TareaEntity) -> TareaEntity:
        asesor_model = None
        if tarea.asignadaA:
            asesor_model = AsesorModel.objects.filter(
                email_asesor=tarea.asignadaA.emailAsesor
            ).first()

        model, _ = TareaModel.objects.update_or_create(
            id_tarea=tarea.idTarea,
            defaults={
                'titulo': tarea.titulo,
                'prioridad': tarea.prioridad.value,
                'estado': tarea.estado.value,
                'vencimiento': tarea.vencimiento,
                'comentario': tarea.comentario,
                'asignada_a': asesor_model,
            }
        )
        return self._to_entity(model)

    def obtener_por_id(self, id_tarea: str) -> Optional[TareaEntity]:
        try:
            model = TareaModel.objects.select_related('asignada_a').get(id_tarea=id_tarea)
            return self._to_entity(model)
        except TareaModel.DoesNotExist:
            return None

    def listar_todas(self) -> List[TareaEntity]:
        return [
            self._to_entity(m) for m in
            TareaModel.objects.select_related('asignada_a').all()
        ]

    def listar_por_estado(self, estado: EstadoTarea) -> List[TareaEntity]:
        return [
            self._to_entity(m) for m in
            TareaModel.objects.filter(estado=estado.value)
        ]

    def listar_por_prioridad(self, prioridad: PrioridadTarea) -> List[TareaEntity]:
        return [
            self._to_entity(m) for m in
            TareaModel.objects.filter(prioridad=prioridad.value)
        ]

    def listar_por_asesor(self, email_asesor: str) -> List[TareaEntity]:
        return [
            self._to_entity(m) for m in
            TareaModel.objects.filter(asignada_a__email_asesor=email_asesor)
        ]

    def listar_por_solicitud(self, solicitud_codigo: str) -> List[TareaEntity]:
        return [
            self._to_entity(m) for m in
            TareaModel.objects.filter(solicitud__codigo=solicitud_codigo)
        ]

    def listar_vencidas(self) -> List[TareaEntity]:
        now = datetime.now()
        return [
            self._to_entity(m) for m in
            TareaModel.objects.filter(
                vencimiento__lt=now
            ).exclude(
                estado=EstadoTarea.COMPLETADA.value
            )
        ]

    def listar_por_vencer(self, horas: int = 24) -> List[TareaEntity]:
        now = datetime.now()
        limite = now + timedelta(hours=horas)
        return [
            self._to_entity(m) for m in
            TareaModel.objects.filter(
                vencimiento__gte=now,
                vencimiento__lte=limite
            ).exclude(
                estado=EstadoTarea.COMPLETADA.value
            )
        ]

    def eliminar(self, id_tarea: str) -> bool:
        deleted, _ = TareaModel.objects.filter(id_tarea=id_tarea).delete()
        return deleted > 0

    def existe(self, id_tarea: str) -> bool:
        return TareaModel.objects.filter(id_tarea=id_tarea).exists()


# ========================================
# Repositorio: DjangoCitaRepository
# ========================================
class DjangoCitaRepository(CitaRepository):
    """Implementación Django ORM del repositorio de Cita"""

    def _to_entity(self, model: CitaModel) -> CitaEntity:
        return CitaEntity(
            idCita=model.id_cita,
            solicitudCodigo=model.solicitud.codigo,
            observacion=model.observacion,
            rango=RangoFechaHora(inicio=model.inicio, fin=model.fin),
            tipo=TipoCita(model.tipo),
            estado=EstadoCita(model.estado),
        )

    def guardar(self, cita: CitaEntity) -> CitaEntity:
        solicitud = SolicitudMigratoriaModel.objects.get(codigo=cita.solicitudCodigo)
        model, _ = CitaModel.objects.update_or_create(
            id_cita=cita.idCita,
            defaults={
                'solicitud': solicitud,
                'observacion': cita.observacion,
                'tipo': cita.tipo.value,
                'estado': cita.estado.value,
                'inicio': cita.rango.inicio,
                'fin': cita.rango.fin,
            }
        )
        return self._to_entity(model)

    def obtener_por_id(self, id_cita: str) -> Optional[CitaEntity]:
        try:
            model = CitaModel.objects.select_related('solicitud').get(id_cita=id_cita)
            return self._to_entity(model)
        except CitaModel.DoesNotExist:
            return None

    def listar_todas(self) -> List[CitaEntity]:
        return [
            self._to_entity(m) for m in
            CitaModel.objects.select_related('solicitud').all()
        ]

    def listar_por_estado(self, estado: EstadoCita) -> List[CitaEntity]:
        return [
            self._to_entity(m) for m in
            CitaModel.objects.filter(estado=estado.value)
        ]

    def listar_por_tipo(self, tipo: TipoCita) -> List[CitaEntity]:
        return [
            self._to_entity(m) for m in
            CitaModel.objects.filter(tipo=tipo.value)
        ]

    def listar_por_solicitud(self, solicitud_codigo: str) -> List[CitaEntity]:
        return [
            self._to_entity(m) for m in
            CitaModel.objects.filter(solicitud__codigo=solicitud_codigo)
        ]

    def listar_por_rango_fecha(self, inicio: datetime, fin: datetime) -> List[CitaEntity]:
        return [
            self._to_entity(m) for m in
            CitaModel.objects.filter(
                Q(inicio__gte=inicio) & Q(inicio__lte=fin)
            )
        ]

    def verificar_disponibilidad(self, inicio: datetime, fin: datetime) -> bool:
        """Verifica que no haya citas que se solapen con el rango dado"""
        conflictos = CitaModel.objects.filter(
            Q(inicio__lt=fin) & Q(fin__gt=inicio)
        ).exclude(
            estado__in=[EstadoCita.CANCELADA.value, EstadoCita.COMPLETADA.value]
        )
        return not conflictos.exists()

    def eliminar(self, id_cita: str) -> bool:
        deleted, _ = CitaModel.objects.filter(id_cita=id_cita).delete()
        return deleted > 0

    def existe(self, id_cita: str) -> bool:
        return CitaModel.objects.filter(id_cita=id_cita).exists()


# ========================================
# Repositorio: DjangoNotificacionRepository
# ========================================
class DjangoNotificacionRepository(NotificacionRepository):
    """Implementación Django ORM del repositorio de Notificacion"""

    def _to_entity(self, model: NotificacionModel) -> NotificacionEntity:
        from SGPM.domain.enums import TipoNotificacion
        entity = NotificacionEntity(
            id_notificacion=model.id_notificacion,
            destinatario=model.destinatario,
            tipo=TipoNotificacion(model.tipo),
            mensaje=model.mensaje,
        )
        entity._leida = model.leida
        entity._creada_en = model.fecha_creacion
        return entity

    def guardar(self, notificacion: NotificacionEntity) -> NotificacionEntity:
        model, _ = NotificacionModel.objects.update_or_create(
            id_notificacion=notificacion._id,
            defaults={
                'destinatario': notificacion.obtener_destinatario(),
                'tipo': notificacion.obtener_tipo().value,
                'mensaje': notificacion.obtener_mensaje(),
                'leida': notificacion.esta_leida(),
            }
        )
        return self._to_entity(model)

    def obtener_por_id(self, id_notificacion: str) -> Optional[NotificacionEntity]:
        try:
            model = NotificacionModel.objects.get(id_notificacion=id_notificacion)
            return self._to_entity(model)
        except NotificacionModel.DoesNotExist:
            return None

    def listar_por_destinatario(self, destinatario: str) -> List[NotificacionEntity]:
        return [
            self._to_entity(m) for m in
            NotificacionModel.objects.filter(destinatario=destinatario)
        ]

    def listar_no_leidas(self, destinatario: str) -> List[NotificacionEntity]:
        return [
            self._to_entity(m) for m in
            NotificacionModel.objects.filter(destinatario=destinatario, leida=False)
        ]

    def marcar_como_leida(self, id_notificacion: str) -> bool:
        updated = NotificacionModel.objects.filter(
            id_notificacion=id_notificacion
        ).update(leida=True)
        return updated > 0

    def eliminar(self, id_notificacion: str) -> bool:
        deleted, _ = NotificacionModel.objects.filter(id_notificacion=id_notificacion).delete()
        return deleted > 0

    def existe(self, id_notificacion: str) -> bool:
        return NotificacionModel.objects.filter(id_notificacion=id_notificacion).exists()
