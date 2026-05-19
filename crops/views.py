from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import CicloCultivo, Especie
import calendar


def fichas_view(request):
    return render(request, "crops/fichas.html")


def fichas_cultivo_list(request):
    """
    Vista para el repositorio de técnicas de cultivo (RF-07, RF-08).
    Permite búsqueda por nombre y filtrado por temporada.
    """
    termino_busqueda = request.GET.get('q', '')
    filtro_temporada = request.GET.get('temporada', '')

    especies = Especie.objects.all()

    if termino_busqueda:
        especies = especies.filter(nombre_comun__icontains=termino_busqueda)

    if filtro_temporada:
        especies = especies.filter(temporada_recomendada=filtro_temporada)

    context = {
        'especies': especies,
        'termino_busqueda': termino_busqueda,
        'filtro_temporada': filtro_temporada,
        'temporadas': ['PRIMAVERA_VERANO', 'OTONIO_INVIERNO', 'ANUAL'],
    }

    return render(request, 'crops/fichas_list.html', context)


def calendario_view(request):
    hoy = timezone.now()
    mes_actual = hoy.month
    anio_actual = hoy.year

    cultivos_del_mes = CicloCultivo.objects.filter(
        fecha_siembra__month=mes_actual,
        fecha_siembra__year=anio_actual,
    ) | CicloCultivo.objects.filter(
        fecha_cosecha_estimada__month=mes_actual,
        fecha_cosecha_estimada__year=anio_actual,
    )

    context = {
        'cultivos': cultivos_del_mes.select_related('especie'),
        'mes_nombre': calendar.month_name[mes_actual].capitalize(),
        'anio': anio_actual,
    }

    return render(request, 'crops/calendario.html', context)


def ficha_detalle_view(request, pk):
    """
    Vista de detalle de una ficha de cultivo (RF-07).
    Muestra todos los campos del modelo Especie.
    Acceso público, sin autenticación requerida.
    """
    especie = get_object_or_404(Especie, pk=pk)
    return render(request, 'crops/ficha_detalle.html', {'especie': especie})
