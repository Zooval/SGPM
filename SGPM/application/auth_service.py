"""
Servicio de autenticación para asesores del sistema SGPM.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from django.contrib.auth.hashers import make_password, check_password

from SGPM.infrastructure.models import Asesor


@dataclass
class AsesorAutenticado:
    """DTO que representa un asesor autenticado en el sistema"""
    email: str
    nombres: str
    apellidos: str
    rol: str
    activo: bool

    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"


class CredencialesInvalidasError(Exception):
    """Error cuando las credenciales son inválidas"""
    pass


class UsuarioInactivoError(Exception):
    """Error cuando el usuario está inactivo"""
    pass


class UsuarioNoEncontradoError(Exception):
    """Error cuando el usuario no existe"""
    pass


class AuthenticationService:
    """
    Servicio de autenticación para asesores.
    Maneja login, logout y verificación de sesión.
    Usa el sistema de hashing de Django (PBKDF2 por defecto).
    """

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Genera un hash seguro de la contraseña usando Django.
        """
        return make_password(password)

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        """Verifica si la contraseña coincide con el hash almacenado"""
        if not stored_hash:
            return False
        return check_password(password, stored_hash)

    def autenticar(self, email: str, password: str) -> AsesorAutenticado:
        """
        Autentifica un asesor con email y contraseña.

        Args:
            email: Correo electrónico del asesor
            password: Contraseña en texto plano

        Returns:
            AsesorAutenticado con los datos del asesor

        Raises:
            UsuarioNoEncontradoError: Si el email no existe
            CredencialesInvalidasError: Si la contraseña es incorrecta
            UsuarioInactivoError: Si el asesor está inactivo
        """
        try:
            asesor = Asesor.objects.get(email_asesor=email)
        except Asesor.DoesNotExist:
            raise UsuarioNoEncontradoError("No existe un usuario con ese correo electrónico")

        # Verificar contraseña
        if not self._verify_password(password, asesor.password_hash):
            raise CredencialesInvalidasError("Correo o contraseña incorrectos")

        # Verificar que esté activo
        if not asesor.activo:
            raise UsuarioInactivoError("Tu cuenta está desactivada. Contacta al administrador.")

        # Actualizar último acceso
        asesor.ultimo_acceso = datetime.now()
        asesor.save(update_fields=['ultimo_acceso'])

        return AsesorAutenticado(
            email=asesor.email_asesor,
            nombres=asesor.nombres,
            apellidos=asesor.apellidos,
            rol=asesor.rol,
            activo=asesor.activo,
        )

    def registrar_asesor(self, email: str, password: str, nombres: str,
                         apellidos: str, rol: str = "ASESOR") -> AsesorAutenticado:
        """
        Registra un nuevo asesor en el sistema.

        Args:
            email: Correo electrónico único
            password: Contraseña en texto plano
            nombres: Nombres del asesor
            apellidos: Apellidos del asesor
            rol: Rol del asesor (ASESOR, ADMIN, OPERADOR)

        Returns:
            AsesorAutenticado con los datos del nuevo asesor
        """
        # Verificar que no exista
        if Asesor.objects.filter(email_asesor=email).exists():
            raise ValueError("Ya existe un usuario con ese correo electrónico")

        # Generar hash de contraseña
        password_hash = self._hash_password(password)

        # Crear asesor
        asesor = Asesor.objects.create(
            email_asesor=email,
            password_hash=password_hash,
            nombres=nombres,
            apellidos=apellidos,
            rol=rol,
            activo=True,
        )

        return AsesorAutenticado(
            email=asesor.email_asesor,
            nombres=asesor.nombres,
            apellidos=asesor.apellidos,
            rol=asesor.rol,
            activo=asesor.activo,
        )

    def cambiar_password(self, email: str, password_actual: str,
                         password_nuevo: str) -> bool:
        """
        Cambia la contraseña de un asesor.

        Args:
            email: Correo del asesor
            password_actual: Contraseña actual
            password_nuevo: Nueva contraseña

        Returns:
            True si se cambió exitosamente
        """
        try:
            asesor = Asesor.objects.get(email_asesor=email)
        except Asesor.DoesNotExist:
            raise UsuarioNoEncontradoError("Usuario no encontrado")

        # Verificar contraseña actual
        if not self._verify_password(password_actual, asesor.password_hash):
            raise CredencialesInvalidasError("La contraseña actual es incorrecta")

        # Generar nuevo hash
        password_hash = self._hash_password(password_nuevo)
        asesor.password_hash = password_hash
        asesor.save(update_fields=['password_hash', 'fecha_actualizacion'])

        return True

    def restablecer_password(self, email: str, password_nuevo: str) -> bool:
        """
        Restablece la contraseña de un asesor (uso administrativo).

        Args:
            email: Correo del asesor
            password_nuevo: Nueva contraseña

        Returns:
            True si se restableció exitosamente
        """
        try:
            asesor = Asesor.objects.get(email_asesor=email)
        except Asesor.DoesNotExist:
            raise UsuarioNoEncontradoError("Usuario no encontrado")

        password_hash = self._hash_password(password_nuevo)
        asesor.password_hash = password_hash
        asesor.save(update_fields=['password_hash', 'fecha_actualizacion'])

        return True

    def obtener_asesor_por_email(self, email: str) -> Optional[AsesorAutenticado]:
        """Obtiene los datos de un asesor por email"""
        try:
            asesor = Asesor.objects.get(email_asesor=email)
            return AsesorAutenticado(
                email=asesor.email_asesor,
                nombres=asesor.nombres,
                apellidos=asesor.apellidos,
                rol=asesor.rol,
                activo=asesor.activo,
            )
        except Asesor.DoesNotExist:
            return None

    def desactivar_asesor(self, email: str) -> bool:
        """Desactiva un asesor"""
        try:
            asesor = Asesor.objects.get(email_asesor=email)
            asesor.activo = False
            asesor.save(update_fields=['activo', 'fecha_actualizacion'])
            return True
        except Asesor.DoesNotExist:
            return False

    def activar_asesor(self, email: str) -> bool:
        """Activa un asesor"""
        try:
            asesor = Asesor.objects.get(email_asesor=email)
            asesor.activo = True
            asesor.save(update_fields=['activo', 'fecha_actualizacion'])
            return True
        except Asesor.DoesNotExist:
            return False
