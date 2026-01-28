from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def solicitante_view(request):
    """
    Vista para gestionar solicitantes
    """
    context = {
        'page_title': 'solicitantes',
    }
    return render(request, 'solicitante/solicitante.html', context)

def registro_solicitante_view(request):
    context = {
        'page_title': 'registro solicitantes',
    }
    return render(request, 'solicitante/registro_solicitante.html', context)

def actualizar_datos_view(request):
    context = {
        'page_title': 'actualizar datos',
    }
    return render(request, 'solicitante/actualizacion_datos.html', context)

def consulta_expedientes_view(request):
    context = {
        'page_title': 'consulta expedientes',
    }
    return render(request, 'solicitante/consulta_expediente.html', context)