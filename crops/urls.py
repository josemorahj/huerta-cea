from django.urls import path
from . import views

app_name = "crops"

urlpatterns = [
    path("", views.fichas_view, name="fichas"),
    path("fichas/", views.fichas_cultivo_list, name="fichas_list"),
    path("calendario/", views.calendario_view, name="calendario"),
]

