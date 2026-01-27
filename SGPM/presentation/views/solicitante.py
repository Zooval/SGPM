from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def solicitante_view(request):
    """
    Vista para gestionar solicitantes
    """
    context = {
        'page_title': 'solicitantes',
    }
    return render(request, 'solicitante.html', context)

