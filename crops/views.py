from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import calendar
from activities.models import Actividad
from .models import Especie, CicloCultivo
from .forms import EspecieForm, CicloCultivoForm

def es_admin(user):
    return user.is_authenticated and getattr(user, 'rol', None) == 'admin'


MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre',
}


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

    actividades_del_mes = Actividad.objects.filter(fecha__month=mes, fecha__year=anio)

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
                'actividades_del_dia': [],
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

                actividades_del_dia = [a for a in actividades_del_mes if a.fecha == fecha_dia]
                dia_info['actividades_del_dia'] = actividades_del_dia

            dias_semana.append(dia_info)
        semanas.append({'dias': dias_semana})

    # ------------------

    context = {
        'cultivos': cultivos_del_mes,
        'semanas': semanas,
        'mes': mes,
        'anio': anio,
        'mes_nombre': MESES_ES[mes],
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


@login_required
def especie_crear_view(request):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('crops:fichas_list')

    if request.method == 'POST':
        form = EspecieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Especie creada correctamente.')
            return redirect('crops:fichas_list')
    else:
        form = EspecieForm()

    return render(request, 'crops/especie_form.html', {'form': form, 'modo': 'crear'})


@login_required
def especie_editar_view(request, pk):
    especie = get_object_or_404(Especie, pk=pk)

    if not es_admin(request.user):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('crops:fichas_list')

    if request.method == 'POST':
        form = EspecieForm(request.POST, request.FILES, instance=especie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Especie actualizada correctamente.')
            return redirect('crops:fichas_list')
    else:
        form = EspecieForm(instance=especie)

    return render(request, 'crops/especie_form.html', {'form': form, 'modo': 'editar', 'especie': especie})


@login_required
def especie_eliminar_view(request, pk):
    especie = get_object_or_404(Especie, pk=pk)

    if not es_admin(request.user):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('crops:fichas_list')

    if request.method == 'POST':
        especie.delete()
        messages.success(request, 'Especie eliminada correctamente.')
        return redirect('crops:fichas_list')

    return render(request, 'crops/especie_confirm_delete.html', {'especie': especie})


@login_required
def ciclo_list_view(request):
    ciclos = CicloCultivo.objects.select_related('especie').all()
    return render(request, 'crops/ciclo_list.html', {'ciclos': ciclos})


@login_required
def ciclo_crear_view(request):
    if not es_admin(request.user):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('crops:ciclo_list')

    if request.method == 'POST':
        form = CicloCultivoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ciclo de cultivo creado correctamente.')
            return redirect('crops:ciclo_list')
    else:
        form = CicloCultivoForm()

    return render(request, 'crops/ciclo_form.html', {'form': form, 'modo': 'crear'})


@login_required
def ciclo_editar_view(request, pk):
    ciclo = get_object_or_404(CicloCultivo, pk=pk)

    if not es_admin(request.user):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('crops:ciclo_list')

    if request.method == 'POST':
        form = CicloCultivoForm(request.POST, instance=ciclo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ciclo de cultivo actualizado correctamente.')
            return redirect('crops:ciclo_list')
    else:
        form = CicloCultivoForm(instance=ciclo)

    return render(request, 'crops/ciclo_form.html', {'form': form, 'modo': 'editar', 'ciclo': ciclo})


@login_required
def ciclo_eliminar_view(request, pk):
    ciclo = get_object_or_404(CicloCultivo, pk=pk)

    if not es_admin(request.user):
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('crops:ciclo_list')

    if request.method == 'POST':
        ciclo.delete()
        messages.success(request, 'Ciclo de cultivo eliminado correctamente.')
        return redirect('crops:ciclo_list')

    return render(request, 'crops/ciclo_confirm_delete.html', {'ciclo': ciclo})

