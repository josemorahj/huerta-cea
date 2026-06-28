from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from .models import Actividad, Inscripcion


def list_view(request):
    """
    Muestra todas las actividades programadas (RF-04, RF-05).
    Las actividades pasadas se muestran al final.
    """
    ahora = timezone.now()

    actividades_programadas = Actividad.objects.filter(
        fecha__gte=ahora.date(),
    ).exclude(estado='CANCELADA').order_by('fecha', 'hora')

    actividades_pasadas = Actividad.objects.filter(
        fecha__lt=ahora.date(),
    ).order_by('-fecha', 'hora')

    context = {
        'actividades_programadas': actividades_programadas,
        'actividades_pasadas': actividades_pasadas,
    }

    return render(request, 'activities/list.html', context)


@login_required
def inscribirse_view(request, actividad_id):
    """
    Inscribe al voluntario autenticado en una actividad (RF-05, RF-06).
    Valida cupo máximo y evita inscripciones duplicadas.
    """
    actividad = get_object_or_404(Actividad, id=actividad_id)

    if request.method == 'POST':
        try:
            inscripcion = Inscripcion(
                actividad=actividad,
                voluntario=request.user,
                estado='CONFIRMADA',
            )
            inscripcion.full_clean()
            inscripcion.save()
            messages.success(
                request,
                f'Te has inscrito correctamente a "{actividad.titulo}".',
            )
        except ValidationError as e:
            for mensaje in e.messages:
                messages.error(request, mensaje)
        except IntegrityError:
            messages.warning(
                request,
                'Ya estás inscrito en esta actividad.',
            )

    return redirect('activities:list')


@login_required
@require_POST
def desinscribirse_view(request, actividad_id):
    """
    Desinscribe al voluntario autenticado de una actividad.
    Busca la inscripción del usuario para la actividad dada y la elimina.
    Si no existe, redirige con mensaje de error.
    """
    try:
        inscripcion = Inscripcion.objects.get(
            actividad_id=actividad_id,
            voluntario=request.user,
        )
        titulo = inscripcion.actividad.titulo
        inscripcion.delete()
        messages.success(
            request,
            f'Te has desinscrito correctamente de "{titulo}".',
        )
    except Inscripcion.DoesNotExist:
        messages.error(
            request,
            'No estás inscrito en esta actividad.',
        )

    return redirect('activities:historial')


@login_required
def historial_view(request):
    """
    Muestra el historial de inscripciones del voluntario autenticado.
    Incluye nombre de la actividad, fecha, estado de inscripción y asistencia.
    """
    inscripciones = Inscripcion.objects.filter(
        voluntario=request.user,
    ).select_related('actividad').order_by('-actividad__fecha', '-actividad__hora')

    return render(request, 'activities/historial.html', {
        'inscripciones': inscripciones,
        'hoy': timezone.now().date(),
    })

