from django.urls import path
from . import views

app_name = "crops"

urlpatterns = [
    path("", views.fichas_view, name="fichas"),
    path("fichas/", views.fichas_cultivo_list, name="fichas_list"),
    path("fichas/<int:pk>/", views.ficha_detalle_view, name="ficha_detalle"),
    path("fichas/crear/", views.especie_crear_view, name="especie_crear"),
    path("fichas/<int:pk>/editar/", views.especie_editar_view, name="especie_editar"),
    path("fichas/<int:pk>/eliminar/", views.especie_eliminar_view, name="especie_eliminar"),
    path("calendario/", views.calendario_view, name="calendario"),
]

