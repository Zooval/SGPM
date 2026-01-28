from django.shortcuts import render, redirect
from django.contrib import messages

from SGPM.application.auth_service import (
    AuthenticationService,
    CredencialesInvalidasError,
    UsuarioInactivoError,
    UsuarioNoEncontradoError,
)


def login_view(request):
    """
    Vista de inicio de sesión para asesores.
    GET: Muestra el formulario de login
    POST: Procesa las credenciales
    """
    # Si ya está autenticado, redirigir al dashboard
    if request.session.get('asesor_email'):
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        # Validar campos vacíos
        if not email or not password:
            messages.error(request, 'Por favor ingresa tu correo y contraseña.')
            return render(request, 'login.html', {'email': email})

        # Intentar autenticar
        auth_service = AuthenticationService()

        try:
            asesor = auth_service.autenticar(email, password)

            # Guardar en sesión
            request.session['asesor_email'] = asesor.email
            request.session['asesor_nombre'] = asesor.nombre_completo()
            request.session['asesor_rol'] = asesor.rol

            # Sesión expira al cerrar navegador
            request.session.set_expiry(0)

            return redirect('dashboard')

        except UsuarioNoEncontradoError:
            messages.error(request, 'Correo o contraseña incorrectos.')
        except CredencialesInvalidasError:
            messages.error(request, 'Correo o contraseña incorrectos.')
        except UsuarioInactivoError as e:
            messages.error(request, str(e))

        return render(request, 'login.html', {'email': email})

    return render(request, 'login.html')


def logout_view(request):
    """
    Cierra la sesión del asesor.
    """
    # Limpiar sesión
    request.session.flush()
    return redirect('login')


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

