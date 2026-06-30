from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('inscribirse/<int:actividad_id>/', views.inscribirse_view, name='inscribirse'),
    path('mi-historial/', views.historial_view, name='historial'),
    path('desinscribirse/<int:actividad_id>/', views.desinscribirse_view, name='desinscribirse'),
    path('crear/', views.crear_view, name='crear'),
    path('editar/<int:actividad_id>/', views.editar_view, name='editar'),
    path('eliminar/<int:actividad_id>/', views.eliminar_view, name='eliminar'),
]
