from django.urls import path
from . import views

app_name='usuarios'
urlpatterns = [
    path('',views.registrar,name='registrar'),
    path('inicioSesion',views.inicioSesion,name='inicioSesion'),
    path('salir',views.salir,name='salir'),
    path('modificar',views.modificar,name='modificar'),
    path('modificarContraseña',views.modificarContraseña,name='modificarContraseña'),
    path('eliminarCuenta',views.eliminarCuenta,name='eliminarCuenta'),
]