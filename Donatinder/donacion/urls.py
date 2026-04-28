from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name='donacion'
urlpatterns = [
    path('inicio', views.inicio, name='inicio'),
    path(
        'explorarDonaciones',
        RedirectView.as_view(pattern_name='donacion:inicio', query_string=False),
        name='explorarDonaciones_legacy',
    ),
    path('ingresarDonacion',views.ingresarDonacion,name='ingresarDonacion'),
    path('verDonaciones/<int:userId>',views.verDonaciones,name='verDonaciones'),
    #path('confirmarDonacion/<int:userId>',views.confirmarDonacion,name='confirmarDonacion'),
    path('confirmarDonacion/<int:donacionId>',views.confirmarDonacion,name='confirmarDonacion'),
    path('ayuda',views.ayuda,name='ayuda'),
    path('modificarDonacion/<int:donacionId>',views.modificarDonacion,name='modificarDonacion'),
    path('eliminarDonacion/<int:donacionId>',views.eliminarDonacion,name='eliminarDonacion'),
]
