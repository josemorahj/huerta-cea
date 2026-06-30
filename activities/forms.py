from django import forms
from .models import Actividad


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['titulo', 'descripcion', 'fecha', 'hora', 'lugar', 'cupo_maximo', 'responsable', 'estado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
