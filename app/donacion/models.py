from django.db import models
from usuarios.models import CustomUser

ELECCION_ESTADO = [
    (1, 'Nuevo'),
    (2, 'Usado'),
    (3, 'Dañado'),
]


class Donacion(models.Model):
    class EstadoPublicacion(models.IntegerChoices):
        ACTIVA = 1, 'Activa'
        RESERVADA = 2, 'Reservada'
        ENTREGADA = 3, 'Entregada'

    nombre = models.CharField(max_length=20)
    estado = models.IntegerField(choices=ELECCION_ESTADO, default=1, null=False, blank=False)
    descripcion = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='imagenes/')
    donador = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    retirado = models.BooleanField(default=False)
    mostrar_en_feed = models.BooleanField(
        default=True,
        help_text='Si está en False, la donación no aparece en el feed de otros (p. ej. reservada).',
    )
    estado_publicacion = models.IntegerField(
        choices=EstadoPublicacion.choices,
        default=EstadoPublicacion.ACTIVA,
    )
    reservado_con = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='donaciones_en_reserva',
        help_text='Interesado elegido cuando la publicación está reservada o entregada.',
    )


class DecisionDonacion(models.Model):
    class Tipo(models.IntegerChoices):
        INTERES = 1, 'Interesado'
        PASS = 2, 'No me interesa'

    usuario = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='decisiones_donacion'
    )
    donacion = models.ForeignKey(Donacion, on_delete=models.CASCADE, related_name='decisiones')
    tipo = models.IntegerField(choices=Tipo.choices)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('usuario', 'donacion'), name='unique_decision_usuario_donacion'),
        ]


class Conversacion(models.Model):
    donacion = models.ForeignKey(Donacion, on_delete=models.CASCADE, related_name='conversaciones')
    interesado = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='conversaciones_como_interesado'
    )
    creado = models.DateTimeField(auto_now_add=True)
    escritura_bloqueada = models.BooleanField(
        default=False,
        help_text='Si es True, no se pueden enviar mensajes (p. ej. donación ya entregada a otro).',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('donacion', 'interesado'),
                name='unique_conversacion_donacion_interesado',
            ),
        ]


class Mensaje(models.Model):
    conversacion = models.ForeignKey(
        Conversacion, on_delete=models.CASCADE, related_name='mensajes'
    )
    autor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mensajes_enviados')
    cuerpo = models.TextField(max_length=2000)
    creado = models.DateTimeField(auto_now_add=True)


class UsuarioBloqueo(models.Model):
    bloqueador = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='bloqueos_emitidos'
    )
    bloqueado = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='bloqueos_recibidos'
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('bloqueador', 'bloqueado'), name='unique_usuario_bloqueo_par'
            ),
        ]


class ConversacionOcultaPorUsuario(models.Model):
    usuario = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='conversaciones_ocultas'
    )
    conversacion = models.ForeignKey(
        Conversacion, on_delete=models.CASCADE, related_name='ocultaciones'
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('usuario', 'conversacion'), name='unique_conversacion_oculta_usuario'
            ),
        ]


class Denuncia(models.Model):
    denunciante = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='denuncias_realizadas'
    )
    conversacion = models.ForeignKey(
        Conversacion, on_delete=models.CASCADE, related_name='denuncias'
    )
    comentario = models.CharField(max_length=500, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
