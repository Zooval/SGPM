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
        remember = request.POST.get('remember')

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

            # Configurar duración de la sesión
            if remember:
                # Sesión dura 30 días
                request.session.set_expiry(60 * 60 * 24 * 30)
            else:
                # Sesión expira al cerrar navegador
                request.session.set_expiry(0)

            messages.success(request, f'¡Bienvenido, {asesor.nombres}!')
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
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')
