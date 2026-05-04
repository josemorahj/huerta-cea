from django.contrib import admin
from .models import Especie, CicloCultivo


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_comun',
        'nombre_cientifico',
        'temporada_recomendada',
        'frecuencia_riego',
    )
    search_fields = ('nombre_comun', 'nombre_cientifico')
    list_filter = ('temporada_recomendada',)


@admin.register(CicloCultivo)
class CicloCultivoAdmin(admin.ModelAdmin):
    list_display = (
        'especie',
        'fecha_siembra',
        'fecha_cosecha_estimada',
        'estado',
    )
    list_filter = ('estado', 'especie', 'fecha_siembra')
    search_fields = ('especie__nombre_comun',)

    fieldsets = (
        ('Información del Ciclo', {
            'fields': ('especie', 'estado', 'observaciones'),
        }),
        ('Cronograma', {
            'fields': ('fecha_siembra', 'fecha_cosecha_estimada'),
        }),
    )
