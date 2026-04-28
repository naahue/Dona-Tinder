from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class RegistroForm(UserCreationForm):

    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Nombre'}), label='')
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Apellido'}), label='')
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Email'}), label='', required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Contraseña','title':'''Ayuda: La contraseña es muy similar a nombre
            La contraseña es demasiado corta. Debe contener por lo menos 8 caracteres
            La contraseña tiene un valor demasiado común'''}), label='', required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirmar contraseña','title':'Ayuda: La contraseñas deben coincidir'}), label='', required=True)

    class Meta:
        model=get_user_model()
        fields=['first_name','last_name','email','password1','password2']
    
    def save(self,commit=True):
        user=super(RegistroForm,self).save(commit=False)
        user.email=self.cleaned_data['email']
        if commit:
            user.save()
        return user

class InicioSesionForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Email'}), label='', required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Contraseña'}), label='', required=True)

class ModificarDatosForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Nombre'}), label='')
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Apellido'}), label='')

class ModificarContraseñaForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Contraseña'}), label='', required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirmar contraseña'}), label='', required=True)
    
    class Meta:
        model=get_user_model()
        fields=['password1','password2']
