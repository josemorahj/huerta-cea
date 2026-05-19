from django.urls import path
from . import views

app_name = "crops"

urlpatterns = [
    path("", views.fichas_view, name="fichas"),
    path("fichas/", views.fichas_cultivo_list, name="fichas_list"),
    path("fichas/<int:pk>/", views.ficha_detalle_view, name="ficha_detalle"),
    path("calendario/", views.calendario_view, name="calendario"),
]

