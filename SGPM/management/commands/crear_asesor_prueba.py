"""
Comando para crear un asesor de prueba.
Uso: python manage.py crear_asesor_prueba
"""
from django.core.management.base import BaseCommand
from SGPM.application.auth_service import AuthenticationService


class Command(BaseCommand):
    help = 'Crea un asesor de prueba para desarrollo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            default='admin@sgpm.com',
            help='Email del asesor (default: admin@sgpm.com)'
        )
        parser.add_argument(
            '--password',
            default='admin123',
            help='Contraseña del asesor (default: admin123)'
        )
        parser.add_argument(
            '--nombres',
            default='Administrador',
            help='Nombres del asesor (default: Administrador)'
        )
        parser.add_argument(
            '--apellidos',
            default='Sistema',
            help='Apellidos del asesor (default: Sistema)'
        )
        parser.add_argument(
            '--rol',
            default='ADMIN',
            choices=['ASESOR', 'ADMIN', 'OPERADOR'],
            help='Rol del asesor (default: ADMIN)'
        )

    def handle(self, *args, **options):
        auth_service = AuthenticationService()

        email = options['email']
        password = options['password']
        nombres = options['nombres']
        apellidos = options['apellidos']
        rol = options['rol']

        try:
            asesor = auth_service.registrar_asesor(
                email=email,
                password=password,
                nombres=nombres,
                apellidos=apellidos,
                rol=rol,
            )

            self.stdout.write(self.style.SUCCESS(
                f'\n✓ Asesor creado exitosamente:\n'
                f'  Email: {asesor.email}\n'
                f'  Nombre: {asesor.nombre_completo()}\n'
                f'  Rol: {asesor.rol}\n'
                f'  Contraseña: {password}\n'
            ))

        except ValueError as e:
            self.stdout.write(self.style.WARNING(f'\n⚠ {e}'))

            # Ofrecer restablecer contraseña
            self.stdout.write('¿Desea restablecer la contraseña? (s/n): ', ending='')
            respuesta = input().strip().lower()

            if respuesta == 's':
                auth_service.restablecer_password(email, password)
                self.stdout.write(self.style.SUCCESS(
                    f'\n✓ Contraseña restablecida a: {password}'
                ))
