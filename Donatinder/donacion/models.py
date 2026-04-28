from django.db import models
from usuarios.models import CustomUser

ELECCION_ESTADO = [
    (1, 'Nuevo'),
    (2, 'Usado'),
    (3, 'Dañado'),
]


class Donacion(models.Model):
    nombre = models.CharField(max_length=20)
    estado = models.IntegerField(choices=ELECCION_ESTADO, default=1, null=False, blank=False)
    descripcion = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='imagenes/')
    donador = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    retirado = models.BooleanField(default=False)
