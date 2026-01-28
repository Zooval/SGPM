from django.shortcuts import render, redirect, get_object_or_404
from SGPM.domain.enums import EstadoTarea, PrioridadTarea

def listar_tareas_view(request):
    """
    Lista todas las tareas
    """
    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
    }
    return render(request, 'tareas/listar.html', context)
    
def crear_tarea_view(request):
    """
    Crea una nueva tarea
    """
    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
        'estados': list(EstadoTarea),
        'prioridades': list(PrioridadTarea),
    }
    return render(request, 'tareas/crear.html', context)
    
    
def editar_tarea_view(request, tarea_id):
    """
    Edita una tarea
    """
    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
        'estados': list(EstadoTarea),
        'prioridades': list(PrioridadTarea),
    }
    return render(request, 'tareas/editar.html', context)
    
def eliminar_tarea_view(request, tarea_id):
    """
    Elimina una tarea
    """
    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
    }
    return render(request, 'tareas/eliminar.html', context)
    
def reportes_tareas_view(request):
    """
    Muestra reportes estadísticos de tareas (solo ADMIN)
    """
    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
    }
    return render(request, 'tareas/reportes.html', context)