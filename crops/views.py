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


def _calcular_navegacion_mes(mes, anio):
    """Calcula mes/anterior, mes/siguiente (con ajuste de año)."""
    from datetime import date

    # Mes anterior
    if mes == 1:
        mes_anterior, anio_anterior = 12, anio - 1
    else:
        mes_anterior, anio_anterior = mes - 1, anio

    # Mes siguiente
    if mes == 12:
        mes_siguiente, anio_siguiente = 1, anio + 1
    else:
        mes_siguiente, anio_siguiente = mes + 1, anio

    return mes_anterior, anio_anterior, mes_siguiente, anio_siguiente


def calendario_view(request):
    from datetime import date

    hoy = timezone.now()

    # Parámetros GET opcionales
    try:
        mes = int(request.GET.get('mes', hoy.month))
    except (ValueError, TypeError):
        mes = hoy.month

    try:
        anio = int(request.GET.get('anio', hoy.year))
    except (ValueError, TypeError):
        anio = hoy.year

    # Calcular navegación
    mes_anterior, anio_anterior, mes_siguiente, anio_siguiente = (
        _calcular_navegacion_mes(mes, anio)
    )

    cultivos_del_mes = CicloCultivo.objects.filter(
        fecha_siembra__month=mes,
        fecha_siembra__year=anio,
    ) | CicloCultivo.objects.filter(
        fecha_cosecha_estimada__month=mes,
        fecha_cosecha_estimada__year=anio,
    )

    cultivos_del_mes = cultivos_del_mes.select_related('especie')

    # --- Generar estructura de semanas para la cuadrícula ---
    cal = calendar.Calendar(firstweekday=0)  # Lunes como primer día
    semanas_raw = cal.monthdayscalendar(anio, mes)

    hoy_local = hoy.date()
    semanas = []

    for semana in semanas_raw:
        dias_semana = []
        for numero_dia in semana:
            dia_info = {
                'numero_dia': numero_dia,
                'cultivos_del_dia': [],
                'es_hoy': False,
            }
            if numero_dia != 0:
                fecha_dia = date(anio, mes, numero_dia)
                dia_info['es_hoy'] = (fecha_dia == hoy_local)

                # Cultivos cuya siembra o cosecha coincide exactamente con este día
                cultivos_del_dia = [
                    c for c in cultivos_del_mes
                    if c.fecha_siembra == fecha_dia or c.fecha_cosecha_estimada == fecha_dia
                ]
                dia_info['cultivos_del_dia'] = cultivos_del_dia

            dias_semana.append(dia_info)
        semanas.append({'dias': dias_semana})

    # ------------------

    context = {
        'cultivos': cultivos_del_mes,
        'semanas': semanas,
        'mes': mes,
        'anio': anio,
        'mes_nombre': calendar.month_name[mes].capitalize(),
        'mes_anterior': mes_anterior,
        'anio_anterior': anio_anterior,
        'mes_siguiente': mes_siguiente,
        'anio_siguiente': anio_siguiente,
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

