from django.core.checks import messages
from django.shortcuts import render, redirect

def dashboard_view(request):
    """
    Vista del dashboard (requiere autenticación).
    """
    # Verificar autenticación
    if not request.session.get('asesor_email'):
        messages.warning(request, 'Debes iniciar sesión para acceder.')
        return redirect('login')

    context = {
        'asesor_nombre': request.session.get('asesor_nombre'),
        'asesor_email': request.session.get('asesor_email'),
        'asesor_rol': request.session.get('asesor_rol'),
    }

    return render(request, 'dashboard.html', context)