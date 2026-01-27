from django.db import models
from django.core.validators import URLValidator
from datetime import datetime

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


# ========================================
# Modelo: Solicitante
# ========================================
class Solicitante(models.Model):
    """Representa a un solicitante/migrante"""

    cedula = models.CharField(max_length=20, unique=True, null=False)
    nombres = models.CharField(max_length=100, null=False)
    apellidos = models.CharField(max_length=100, null=False)
    correo = models.EmailField(null=False)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'solicitante'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.cedula})"

    def obtener_nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


# ========================================
# Modelo: Asesor
# ========================================
class Asesor(models.Model):
    """Representa un asesor del sistema"""

    ROL_CHOICES = [(rol.value, rol.value) for rol in RolUsuario]

    nombres = models.CharField(max_length=100, null=False)
    apellidos = models.CharField(max_length=100, null=False)
    email_asesor = models.EmailField(unique=True, null=False)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default=RolUsuario.ASESOR.value)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'asesor'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.email_asesor})"

    def obtener_nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


# ========================================
# Modelo: SolicitudMigratoria
# ========================================
class SolicitudMigratoria(models.Model):
    """Representa una solicitud migratoria"""

    TIPO_SERVICIO_CHOICES = [(tipo.value, tipo.value) for tipo in TipoServicio]
    ESTADO_SOLICITUD_CHOICES = [(estado.value, estado.value) for estado in EstadoSolicitud]

    codigo = models.CharField(max_length=50, unique=True, null=False, primary_key=True)
    tipo_servicio = models.CharField(
        max_length=20,
        choices=TIPO_SERVICIO_CHOICES,
        null=True,
        blank=True
    )
    estado_actual = models.CharField(
        max_length=30,
        choices=ESTADO_SOLICITUD_CHOICES,
        default=EstadoSolicitud.CREADA.value
    )
    solicitante = models.ForeignKey(
        Solicitante,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='solicitudes'
    )
    asesor = models.ForeignKey(
        Asesor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_asignadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    # Fechas del proceso
    fecha_recepcion_docs = models.DateField(null=True, blank=True)
    fecha_envio_solicitud = models.DateField(null=True, blank=True)
    fecha_cita = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'solicitud_migratoria'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Solicitud {self.codigo} - {self.estado_actual}"


# ========================================
# Modelo: Documento
# ========================================
class Documento(models.Model):
    """Representa un documento de la solicitud"""

    TIPO_DOCUMENTO_CHOICES = [(tipo.value, tipo.value) for tipo in TipoDocumento]
    ESTADO_DOCUMENTO_CHOICES = [(estado.value, estado.value) for estado in EstadoDocumento]

    id_documento = models.CharField(max_length=50, unique=True, primary_key=True)
    solicitud = models.ForeignKey(
        SolicitudMigratoria,
        on_delete=models.CASCADE,
        related_name='documentos'
    )
    solicitante = models.ForeignKey(
        Solicitante,
        on_delete=models.CASCADE,
        related_name='documentos',
        null=True,
        blank=True
    )
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_DOCUMENTO_CHOICES,
        null=False
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_DOCUMENTO_CHOICES,
        default=EstadoDocumento.RECIBIDO.value
    )
    fecha_expiracion = models.DateField(null=True, blank=True)
    version_actual = models.IntegerField(default=1)
    observacion = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documento'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Documento {self.id_documento} - {self.tipo}"


# ========================================
# Modelo: Tarea
# ========================================
class Tarea(models.Model):
    """Representa una tarea asignada a un asesor"""

    ESTADO_TAREA_CHOICES = [(estado.value, estado.value) for estado in EstadoTarea]
    PRIORIDAD_TAREA_CHOICES = [(prioridad.value, prioridad.value) for prioridad in PrioridadTarea]

    id_tarea = models.CharField(max_length=50, unique=True, primary_key=True)
    solicitud = models.ForeignKey(
        SolicitudMigratoria,
        on_delete=models.CASCADE,
        related_name='tareas',
        null=True,
        blank=True
    )
    titulo = models.CharField(max_length=200, null=False)
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_TAREA_CHOICES,
        null=False
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_TAREA_CHOICES,
        default=EstadoTarea.PENDIENTE.value
    )
    vencimiento = models.DateTimeField(null=True, blank=True)
    comentario = models.TextField(blank=True)
    asignada_a = models.ForeignKey(
        Asesor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tareas_asignadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tarea'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Tarea {self.id_tarea} - {self.titulo}"


# ========================================
# Modelo: Cita
# ========================================
class Cita(models.Model):
    """Representa una cita migratoria"""

    TIPO_CITA_CHOICES = [(tipo.value, tipo.value) for tipo in TipoCita]
    ESTADO_CITA_CHOICES = [(estado.value, estado.value) for estado in EstadoCita]

    id_cita = models.CharField(max_length=50, unique=True, primary_key=True)
    solicitud = models.ForeignKey(
        SolicitudMigratoria,
        on_delete=models.CASCADE,
        related_name='citas'
    )
    observacion = models.TextField(blank=True)
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CITA_CHOICES,
        null=False
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CITA_CHOICES,
        default=EstadoCita.PROGRAMADA.value
    )
    inicio = models.DateTimeField(null=False)
    fin = models.DateTimeField(null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cita'
        ordering = ['-fecha_creacion']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(fin__gt=models.F('inicio')),
                name='cita_fin_mayor_que_inicio'
            )
        ]

    def __str__(self):
        return f"Cita {self.id_cita} - {self.tipo}"


# ========================================
# Modelo: Notificacion
# ========================================
class Notificacion(models.Model):
    """Representa una notificación del sistema"""

    TIPO_NOTIFICACION_CHOICES = [(tipo.value, tipo.value) for tipo in TipoNotificacion]

    id_notificacion = models.CharField(max_length=50, unique=True, primary_key=True)
    destinatario = models.EmailField(null=False)
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_NOTIFICACION_CHOICES,
        null=False
    )
    mensaje = models.TextField(null=False)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notificacion'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Notificación {self.id_notificacion} - {self.tipo}"


# ========================================
# Modelo: HistorialEstadoSolicitud
# ========================================
class HistorialEstadoSolicitud(models.Model):
    """Mantiene un registro de los cambios de estado de las solicitudes"""

    solicitud = models.ForeignKey(
        SolicitudMigratoria,
        on_delete=models.CASCADE,
        related_name='historial_estados'
    )
    usuario = models.CharField(max_length=100, null=False)
    estado_anterior = models.CharField(max_length=30, null=False)
    estado_nuevo = models.CharField(max_length=30, null=False)
    motivo = models.TextField(blank=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historial_estado_solicitud'
        ordering = ['-fecha_cambio']

    def __str__(self):
        return f"Cambio {self.estado_anterior} -> {self.estado_nuevo} ({self.fecha_cambio})"


# ========================================
# Modelo: HistorialFechaProceso
# ========================================
class HistorialFechaProceso(models.Model):
    """Mantiene un registro de los cambios en las fechas del proceso"""

    solicitud = models.ForeignKey(
        SolicitudMigratoria,
        on_delete=models.CASCADE,
        related_name='historial_fechas'
    )
    usuario = models.CharField(max_length=100, null=False)
    campo = models.CharField(max_length=50, null=False)
    valor_anterior = models.DateField(null=True, blank=True)
    valor_nuevo = models.DateField(null=False)
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historial_fecha_proceso'
        ordering = ['-fecha_cambio']

    def __str__(self):
        return f"Cambio {self.campo}: {self.valor_anterior} -> {self.valor_nuevo}"

