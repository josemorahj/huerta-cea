from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registro/', views.register_view, name='register'),
    path('iniciar-sesion/', views.login_view, name='login'),
    path('cerrar-sesion/', views.logout_view, name='logout'),
    path('usuarios/', views.usuario_list_view, name='usuario_list'),
    path('usuarios/crear/', views.usuario_crear_view, name='usuario_crear'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar_view, name='usuario_editar'),
    path('usuarios/<int:pk>/eliminar/', views.usuario_eliminar_view, name='usuario_eliminar'),
]