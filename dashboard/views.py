from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from accounts.models import User
from activities.models import Actividad
from crops.models import CicloCultivo


@login_required
def home_view(request):
    """
    Panel de administración con métricas clave (RF-02, RF-10).
    Solo accesible para usuarios con rol admin.
    """
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para acceder al panel de administración.')
        return redirect('activities:list')

    ahora = timezone.now()
    mes_actual = ahora.month
    anio_actual = ahora.year

    total_voluntarios = User.objects.filter(rol='voluntario').count()

    actividades_del_mes = Actividad.objects.filter(
        fecha__month=mes_actual,
        fecha__year=anio_actual,
    ).count()

    cultivos_activos = CicloCultivo.objects.filter(
        estado__in=['SEMBRADO', 'EN_CRECIMIENTO'],
    ).count()

    context = {
        'total_voluntarios': total_voluntarios,
        'actividades_del_mes': actividades_del_mes,
        'cultivos_activos': cultivos_activos,
    }

    return render(request, 'dashboard/home.html', context)

