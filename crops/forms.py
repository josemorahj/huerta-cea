from django import forms
from .models import Especie, CicloCultivo


class EspecieForm(forms.ModelForm):
    class Meta:
        model = Especie
        fields = [
            'nombre_comun',
            'nombre_cientifico',
            'descripcion',
            'condiciones_cultivo',
            'frecuencia_riego',
            'temporada_recomendada',
            'imagen',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'condiciones_cultivo': forms.Textarea(attrs={'rows': 4}),
        }


class CicloCultivoForm(forms.ModelForm):
    class Meta:
        model = CicloCultivo
        fields = [
            'especie',
            'fecha_siembra',
            'fecha_cosecha_estimada',
            'estado',
            'observaciones',
        ]
        widgets = {
            'fecha_siembra': forms.DateInput(attrs={'type': 'date'}),
            'fecha_cosecha_estimada': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
