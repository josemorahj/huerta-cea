from django.core.management.base import BaseCommand
from decouple import config
from accounts.models import User


class Command(BaseCommand):
    help = 'Crea o actualiza un superusuario en produccion usando variables de entorno.'

    def handle(self, *args, **options):
        username = config('DJANGO_SUPERUSER_USERNAME', default='')
        email = config('DJANGO_SUPERUSER_EMAIL', default='')
        password = config('DJANGO_SUPERUSER_PASSWORD', default='')

        if not all([username, email, password]):
            self.stdout.write(
                self.style.WARNING(
                    'Variables de entorno DJANGO_SUPERUSER_USERNAME, '
                    'DJANGO_SUPERUSER_EMAIL y DJANGO_SUPERUSER_PASSWORD '
                    'no estan configuradas. Se omite la creacion del superusuario.'
                )
            )
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_superuser': True,
                'is_staff': True,
            },
        )

        if not created:
            user.email = email
            user.is_superuser = True
            user.is_staff = True

        user.set_password(password)
        user.save(update_fields=['email', 'password', 'is_superuser', 'is_staff'])

        action = 'creado' if created else 'actualizada'
        self.stdout.write(
            self.style.SUCCESS(
                f'Superusuario "{username}" {action} exitosamente.'
            )
        )
