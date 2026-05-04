from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings


class Actividad(models.Model):
    """
    Representa una actividad programada en la huerta comunitaria (RF-04, RF-05, RF-06).
    """

    ESTADO_OPCIONES = [
        ('PROGRAMADA', 'Programada'),
        ('EN_CURSO', 'En curso'),
        ('FINALIZADA', 'Finalizada'),
        ('CANCELADA', 'Cancelada'),
    ]

    titulo = models.CharField(
        max_length=200,
        verbose_name='Título',
        help_text='Nombre descriptivo de la actividad.',
    )
    descripcion = models.TextField(
        verbose_name='Descripción',
        help_text='Detalles y objetivos de la actividad.',
    )
    fecha = models.DateField(
        verbose_name='Fecha',
        help_text='Día en que se realizará la actividad.',
    )
    hora = models.TimeField(
        verbose_name='Hora',
        help_text='Horario de inicio de la actividad.',
    )
    lugar = models.CharField(
        max_length=200,
        verbose_name='Lugar',
        help_text='Ubicación dentro del CEA donde se realizará.',
    )
    cupo_maximo = models.PositiveIntegerField(
        verbose_name='Cupo máximo',
        help_text='Número máximo de voluntarios que pueden participar.',
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='actividades_responsable',
        verbose_name='Responsable',
        help_text='Usuario admin encargado de la actividad.',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_OPCIONES,
        default='PROGRAMADA',
        verbose_name='Estado',
        help_text='Etapa actual de la actividad.',
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
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f'{self.titulo} — {self.fecha}'

    @property
    def inscritos_actuales(self):
        """Cantidad de voluntarios inscritos con estado confirmado."""
        return self.inscripciones.filter(estado='CONFIRMADA').count()

    @property
    def cupos_disponibles(self):
        """Cupos restantes para la actividad."""
        return self.cupo_maximo - self.inscritos_actuales


class Inscripcion(models.Model):
    """
    Registro de inscripción de un voluntario a una actividad (RF-05, RF-06).
    """

    ESTADO_OPCIONES = [
        ('CONFIRMADA', 'Confirmada'),
        ('EN_ESPERA', 'En espera'),
        ('CANCELADA', 'Cancelada'),
    ]

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='inscripciones',
        verbose_name='Actividad',
        help_text='Actividad a la que se inscribe el voluntario.',
    )
    voluntario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inscripciones',
        verbose_name='Voluntario',
        help_text='Usuario voluntario que se inscribe.',
    )
    fecha_inscripcion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de inscripción',
        help_text='Momento en que se registró la inscripción.',
    )
    asistio = models.BooleanField(
        default=False,
        verbose_name='Asistió',
        help_text='Indica si el voluntario asistió a la actividad.',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_OPCIONES,
        default='CONFIRMADA',
        verbose_name='Estado',
        help_text='Situación actual de la inscripción.',
    )

    class Meta:
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        ordering = ['-fecha_inscripcion']
        unique_together = ('actividad', 'voluntario')

    def __str__(self):
        return f'{self.voluntario.username} → {self.actividad.titulo} ({self.get_estado_display()})'

    def clean(self):
        """Validación de cupos al confirmar una inscripción."""
        if self.estado == 'CONFIRMADA' and not self.pk:
            if self.actividad.inscritos_actuales >= self.actividad.cupo_maximo:
                raise ValidationError(
                    f'La actividad "{self.actividad.titulo}" ha alcanzado su cupo máximo '
                    f'({self.actividad.cupo_maximo} inscritos).'
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

