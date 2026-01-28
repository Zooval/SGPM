from django.shortcuts import render, redirect
from django.contrib import messages


def solicitante_view(request):
    """
    Vista para gestionar solicitantes
    """
    
    context = {
        'page_title': 'solicitantes',
    }
    return render(request, 'solicitante.html', context)

