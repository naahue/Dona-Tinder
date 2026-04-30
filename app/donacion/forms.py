from django.forms import CharField, Form, ModelForm, Textarea

from .models import Donacion, Mensaje


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


class MensajeForm(ModelForm):
    class Meta:
        model = Mensaje
        fields = ['cuerpo']
        labels = {'cuerpo': 'Mensaje'}
        widgets = {
            'cuerpo': Textarea(
                attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Escribí tu mensaje…'}
            )
        }


class DenunciaForm(Form):
    comentario = CharField(
        label='Detalle opcional',
        max_length=500,
        required=False,
        widget=Textarea(attrs={'rows': 4, 'class': 'form-control'}),
    )
