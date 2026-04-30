from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name = 'donacion'
urlpatterns = [
    path('inicio', views.inicio, name='inicio'),
    path(
        'explorarDonaciones',
        RedirectView.as_view(pattern_name='donacion:inicio', query_string=False),
        name='explorarDonaciones_legacy',
    ),
    path('ingresarDonacion', views.ingresarDonacion, name='ingresarDonacion'),
    path('verDonaciones/<int:userId>', views.verDonaciones, name='verDonaciones'),
    path('confirmarDonacion/<int:donacionId>', views.confirmarDonacion, name='confirmarDonacion'),
    path('ayuda', views.ayuda, name='ayuda'),
    path('mis-likes', views.mis_likes, name='mis_likes'),
    path('mis-chats', views.mis_chats, name='mis_chats'),
    path('mis-chats-ocultos', views.mis_chats_ocultos, name='mis_chats_ocultos'),
    path(
        'chat/<int:conversacionId>/denunciar',
        views.denunciar_conversacion,
        name='denunciar_conversacion',
    ),
    path(
        'chat/<int:conversacionId>/seguridad',
        views.conversacion_seguridad,
        name='conversacion_seguridad',
    ),
    path('chat/<int:conversacionId>', views.chat_conversacion, name='chat_conversacion'),
    path('donacion/<int:donacionId>/chats', views.donacion_chats, name='donacion_chats'),
    path(
        'donacion/<int:donacionId>/donador-accion',
        views.donacion_donador_accion,
        name='donacion_donador_accion',
    ),
    path('modificarDonacion/<int:donacionId>', views.modificarDonacion, name='modificarDonacion'),
    path('eliminarDonacion/<int:donacionId>', views.eliminarDonacion, name='eliminarDonacion'),
    path('api/decision', views.api_registrar_decision, name='api_registrar_decision'),
    path('api/decision/deshacer-pass', views.api_deshacer_pass, name='api_deshacer_pass'),
]
