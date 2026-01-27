from django.contrib import admin
from SGPM.models import (
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


# ========================================
# Admin: Solicitante
# ========================================
@admin.register(Solicitante)
class SolicitanteAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombres', 'apellidos', 'correo', 'telefono', 'fecha_creacion')
    search_fields = ('cedula', 'nombres', 'apellidos', 'correo')
    list_filter = ('fecha_creacion',)
    ordering = ('-fecha_creacion',)


# ========================================
# Admin: Asesor
# ========================================
@admin.register(Asesor)
class AsesorAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'email_asesor', 'rol', 'activo', 'fecha_creacion')
    search_fields = ('nombres', 'apellidos', 'email_asesor')
    list_filter = ('rol', 'activo', 'fecha_creacion')
    ordering = ('-fecha_creacion',)


# ========================================
# Admin: SolicitudMigratoria
# ========================================
@admin.register(SolicitudMigratoria)
class SolicitudMigratoriaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'tipo_servicio', 'estado_actual', 'solicitante', 'asesor', 'fecha_creacion')
    search_fields = ('codigo', 'solicitante__cedula', 'solicitante__nombres', 'asesor__email_asesor')
    list_filter = ('estado_actual', 'tipo_servicio', 'fecha_creacion')
    ordering = ('-fecha_creacion',)
    raw_id_fields = ('solicitante', 'asesor')


# ========================================
# Admin: Documento
# ========================================
@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('id_documento', 'tipo', 'estado', 'solicitud', 'solicitante', 'fecha_creacion')
    search_fields = ('id_documento', 'solicitud__codigo', 'solicitante__cedula')
    list_filter = ('tipo', 'estado', 'fecha_creacion')
    ordering = ('-fecha_creacion',)
    raw_id_fields = ('solicitud', 'solicitante')


# ========================================
# Admin: Tarea
# ========================================
@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ('id_tarea', 'titulo', 'prioridad', 'estado', 'asignada_a', 'vencimiento', 'fecha_creacion')
    search_fields = ('id_tarea', 'titulo', 'asignada_a__email_asesor')
    list_filter = ('prioridad', 'estado', 'fecha_creacion')
    ordering = ('-fecha_creacion',)
    raw_id_fields = ('solicitud', 'asignada_a')


# ========================================
# Admin: Cita
# ========================================
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('id_cita', 'tipo', 'estado', 'solicitud', 'inicio', 'fin', 'fecha_creacion')
    search_fields = ('id_cita', 'solicitud__codigo')
    list_filter = ('tipo', 'estado', 'fecha_creacion')
    ordering = ('-fecha_creacion',)
    raw_id_fields = ('solicitud',)


# ========================================
# Admin: Notificacion
# ========================================
@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id_notificacion', 'tipo', 'destinatario', 'leida', 'fecha_creacion')
    search_fields = ('id_notificacion', 'destinatario', 'mensaje')
    list_filter = ('tipo', 'leida', 'fecha_creacion')
    ordering = ('-fecha_creacion',)


# ========================================
# Admin: HistorialEstadoSolicitud
# ========================================
@admin.register(HistorialEstadoSolicitud)
class HistorialEstadoSolicitudAdmin(admin.ModelAdmin):
    list_display = ('solicitud', 'usuario', 'estado_anterior', 'estado_nuevo', 'fecha_cambio')
    search_fields = ('solicitud__codigo', 'usuario')
    list_filter = ('estado_anterior', 'estado_nuevo', 'fecha_cambio')
    ordering = ('-fecha_cambio',)
    raw_id_fields = ('solicitud',)


# ========================================
# Admin: HistorialFechaProceso
# ========================================
@admin.register(HistorialFechaProceso)
class HistorialFechaProcesoAdmin(admin.ModelAdmin):
    list_display = ('solicitud', 'usuario', 'campo', 'valor_anterior', 'valor_nuevo', 'fecha_cambio')
    search_fields = ('solicitud__codigo', 'usuario', 'campo')
    list_filter = ('campo', 'fecha_cambio')
    ordering = ('-fecha_cambio',)
    raw_id_fields = ('solicitud',)
