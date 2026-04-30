# Estado de publicación (activa/reservada/entregada) y reservado_con

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('donacion', '0006_conversacion_mensaje'),
    ]

    operations = [
        migrations.AddField(
            model_name='donacion',
            name='estado_publicacion',
            field=models.IntegerField(choices=[(1, 'Activa'), (2, 'Reservada'), (3, 'Entregada')], default=1),
        ),
        migrations.AddField(
            model_name='donacion',
            name='reservado_con',
            field=models.ForeignKey(
                blank=True,
                help_text='Interesado elegido cuando la publicación está reservada o entregada.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='donaciones_en_reserva',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
