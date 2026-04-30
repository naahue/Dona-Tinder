from django.contrib import admin

from .models import Conversacion, ConversacionOcultaPorUsuario, DecisionDonacion, Denuncia, Donacion, Mensaje, UsuarioBloqueo


@admin.register(Donacion)
class DonacionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'donador',
        'retirado',
        'estado_publicacion',
        'mostrar_en_feed',
        'reservado_con',
    )


@admin.register(DecisionDonacion)
class DecisionDonacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'donacion', 'tipo', 'creado')
    list_filter = ('tipo',)


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'donacion', 'interesado', 'escritura_bloqueada', 'creado')
    list_select_related = ('donacion', 'interesado')


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversacion', 'autor', 'creado')
    search_fields = ('cuerpo',)


@admin.register(UsuarioBloqueo)
class UsuarioBloqueoAdmin(admin.ModelAdmin):
    list_display = ('id', 'bloqueador', 'bloqueado', 'creado')
    list_select_related = ('bloqueador', 'bloqueado')


@admin.register(ConversacionOcultaPorUsuario)
class ConversacionOcultaPorUsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'conversacion', 'creado')
    list_select_related = ('usuario', 'conversacion')


@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'denunciante', 'conversacion', 'creado')
    list_select_related = ('denunciante', 'conversacion')
    search_fields = ('comentario',)
