from django.contrib import admin
from .models import Actividad, Inscripcion


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'fecha',
        'hora',
        'lugar',
        'cupo_maximo',
        'inscritos_actuales',
        'responsable',
        'estado',
    )
    list_filter = ('estado', 'fecha', 'responsable')
    search_fields = ('titulo', 'descripcion', 'lugar')
    date_hierarchy = 'fecha'

    fieldsets = (
        ('Información General', {
            'fields': ('titulo', 'descripcion', 'lugar'),
        }),
        ('Programación', {
            'fields': ('fecha', 'hora', 'cupo_maximo', 'responsable'),
        }),
        ('Estado', {
            'fields': ('estado',),
        }),
    )


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = (
        'actividad',
        'voluntario',
        'fecha_inscripcion',
        'estado',
        'asistio',
    )
    list_editable = ('asistio',)
    list_filter = ('estado', 'actividad', 'fecha_inscripcion', 'asistio')
    search_fields = (
        'actividad__titulo',
        'voluntario__username',
        'voluntario__email',
    )
    date_hierarchy = 'fecha_inscripcion'

    fieldsets = (
        ('Inscripción', {
            'fields': ('actividad', 'voluntario', 'estado', 'asistio'),
        }),
    )

