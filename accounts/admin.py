from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class UsuarioAdmin(UserAdmin):
    """Personalizacion del admin para el modelo User con rol y telefono."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'rol',
        'telefono',
        'is_staff',
        'is_active',
    )
    list_filter = ('rol', 'is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'telefono')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informacion personal', {
            'fields': ('first_name', 'last_name', 'email', 'telefono', 'rol'),
        }),
        ('Permisos', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'telefono', 'rol',
            ),
        }),
    )
