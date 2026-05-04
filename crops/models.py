from django.db import models
from django.core.exceptions import ValidationError


class Especie(models.Model):
    """
    Repositorio maestro de técnicas de cultivo (RF-07).
    Almacena información de referencia sobre cada especie cultivable.
    """

    TEMPORADA_OPCIONES = [
        ('PRIMAVERA_VERANO', 'Primavera-Verano'),
        ('OTONIO_INVIERNO', 'Otoño-Invierno'),
        ('ANUAL', 'Anual'),
    ]

    nombre_comun = models.CharField(
        max_length=100,
        verbose_name='Nombre común',
        help_text='Nombre con el que se conoce popularmente la especie.',
    )
    nombre_cientifico = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Nombre científico',
        help_text='Nombre científico de la especie (opcional).',
    )
    descripcion = models.TextField(
        verbose_name='Descripción',
        help_text='Descripción general de la especie.',
    )
    condiciones_cultivo = models.TextField(
        verbose_name='Condiciones de cultivo',
        help_text='Detalles de suelo, luz, temperatura y otros requisitos.',
    )
    frecuencia_riego = models.CharField(
        max_length=100,
        verbose_name='Frecuencia de riego',
        help_text='Cada cuánto tiempo se debe regar (ej: "Cada 2 días", "3 veces por semana").',
    )
    temporada_recomendada = models.CharField(
        max_length=30,
        choices=TEMPORADA_OPCIONES,
        verbose_name='Temporada recomendada',
        help_text='Época del año más adecuada para su cultivo.',
    )
    imagen = models.ImageField(
        upload_to='especies/',
        blank=True,
        verbose_name='Imagen',
        help_text='Fotografía de referencia de la especie.',
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización',
    )

    class Meta:
        verbose_name = 'Especie'
        verbose_name_plural = 'Especies'
        ordering = ['nombre_comun']

    def __str__(self):
        return self.nombre_comun


class CicloCultivo(models.Model):
    """
    Representa una instancia real de siembra en la huerta (RF-02, RF-03).
    Núcleo del calendario interactivo de cultivos.
    """

    ESTADO_OPCIONES = [
        ('SEMBRADO', 'Sembrado'),
        ('EN_CRECIMIENTO', 'En crecimiento'),
        ('LISTO_COSECHA', 'Listo para cosecha'),
        ('COSECHADO', 'Cosechado'),
    ]

    especie = models.ForeignKey(
        Especie,
        on_delete=models.CASCADE,
        related_name='ciclos',
        verbose_name='Especie',
        help_text='Especie cultivada en este ciclo.',
    )
    fecha_siembra = models.DateField(
        verbose_name='Fecha de siembra',
        help_text='Día en que se sembró la especie.',
    )
    fecha_cosecha_estimada = models.DateField(
        verbose_name='Fecha estimada de cosecha',
        help_text='Fecha calculada o estimada para la cosecha.',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_OPCIONES,
        default='SEMBRADO',
        verbose_name='Estado',
        help_text='Etapa actual del ciclo de cultivo.',
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones',
        help_text='Notas y resultado final del ciclo (opcional).',
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización',
    )

    class Meta:
        verbose_name = 'Ciclo de cultivo'
        verbose_name_plural = 'Ciclos de cultivo'
        ordering = ['-fecha_siembra']

    def __str__(self):
        return f'{self.especie.nombre_comun} — {self.fecha_siembra}'

    def clean(self):
        """Validación: la fecha de cosecha estimada no puede ser anterior a la siembra."""
        if self.fecha_cosecha_estimada and self.fecha_siembra:
            if self.fecha_cosecha_estimada < self.fecha_siembra:
                raise ValidationError({
                    'fecha_cosecha_estimada': (
                        'La fecha estimada de cosecha no puede ser '
                        'anterior a la fecha de siembra.'
                    ),
                })

    def save(self, *args, **kwargs):
        """Ejecuta la validación antes de guardar."""
        self.full_clean()
        super().save(*args, **kwargs)
