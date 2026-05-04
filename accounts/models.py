from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('voluntario', 'Voluntario'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='voluntario')
    telefono = models.CharField(max_length=15, blank=True)

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_rol_display()})'
