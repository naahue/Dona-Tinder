from django.forms import ModelForm, Textarea
from .models import Donacion


class IngresarDonacionForm(ModelForm):
    class Meta:
        model = Donacion
        fields = ['nombre', 'estado', 'descripcion', 'imagen']
        widgets = {'descripcion': Textarea(attrs={'cols': 50, 'rows': 10})}


class ModificarDonacionForm(ModelForm):
    class Meta:
        model = Donacion
        fields = ['nombre', 'estado', 'descripcion']
        widgets = {'descripcion': Textarea(attrs={'cols': 50, 'rows': 10})}
