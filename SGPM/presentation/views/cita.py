from django.shortcuts import render, redirect
def listar_citas_view(request):
    """
    Lista citas en formato calendario/agenda
    - ADMIN: Ve todas las citas
    - ASESOR: Solo ve sus citas
    """
    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
    }
    return render(request, 'citas/listar.html', context)


def crear_cita_view(request):
    """
    Crea una nueva cita
    """
    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
    }
    return render(request, 'citas/crear.html', context)

def reprogramar_cita_view(request, cita_id):
    """
    Reprograma una cita
    """
    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
    }
    return render(request, 'citas/reprogramar.html', context)
    
    