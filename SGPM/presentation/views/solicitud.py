from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def solicitud_view(request):
    """
    Vista para gestionar solicitudes
    """
    context = {
        'page_title': 'solicitudes',
    }
    return render(request, 'solicitudes/solicitudes.html', context)

@login_required
def listado_view(request):
    context = {
        'page_title': 'listado solicitudes',
    }
    return render(request, 'solicitudes/listado.html', context)