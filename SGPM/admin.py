from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
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
class AsesorCreationForm(forms.ModelForm):
    """Formulario para crear un nuevo asesor con contraseña en texto plano"""
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
        help_text='Ingrese la contraseña en texto plano. Se hasheará automáticamente.'
    )

    class Meta:
        model = Asesor
        fields = ('nombres', 'apellidos', 'email_asesor', 'rol', 'activo')

    def save(self, commit=True):
        asesor = super().save(commit=False)
        asesor.password_hash = make_password(self.cleaned_data['password'])
        if commit:
            asesor.save()
        return asesor


class AsesorChangeForm(forms.ModelForm):
    """Formulario para editar un asesor existente"""
    password = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput,
        required=False,
        help_text='Deje en blanco para mantener la contraseña actual. Ingrese una nueva para cambiarla.'
    )

    class Meta:
        model = Asesor
        fields = ('nombres', 'apellidos', 'email_asesor', 'rol', 'activo')

    def save(self, commit=True):
        asesor = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            asesor.password_hash = make_password(password)
        if commit:
            asesor.save()
        return asesor


@admin.register(Asesor)
class AsesorAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'email_asesor', 'rol', 'activo', 'fecha_creacion')
    search_fields = ('nombres', 'apellidos', 'email_asesor')
    list_filter = ('rol', 'activo', 'fecha_creacion')
    ordering = ('-fecha_creacion',)

    # Excluir password_hash de los formularios
    exclude = ('password_hash',)

    def get_form(self, request, obj=None, **kwargs):
        """Usar formulario de creación o edición según corresponda"""
        if obj is None:
            # Creando nuevo asesor
            kwargs['form'] = AsesorCreationForm
        else:
            # Editando asesor existente
            kwargs['form'] = AsesorChangeForm
        return super().get_form(request, obj, **kwargs)


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
