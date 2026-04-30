# UsuarioBloqueo, ConversacionOcultaPorUsuario, Denuncia

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('donacion', '0008_sync_mostrar_feed_estado'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsuarioBloqueo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                (
                    'bloqueado',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='bloqueos_recibidos',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'bloqueador',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='bloqueos_emitidos',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='ConversacionOcultaPorUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                (
                    'conversacion',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='ocultaciones',
                        to='donacion.conversacion',
                    ),
                ),
                (
                    'usuario',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='conversaciones_ocultas',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Denuncia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comentario', models.CharField(blank=True, max_length=500)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                (
                    'conversacion',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='denuncias',
                        to='donacion.conversacion',
                    ),
                ),
                (
                    'denunciante',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='denuncias_realizadas',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name='usuariobloqueo',
            constraint=models.UniqueConstraint(
                fields=('bloqueador', 'bloqueado'),
                name='unique_usuario_bloqueo_par',
            ),
        ),
        migrations.AddConstraint(
            model_name='conversacionocultaporusuario',
            constraint=models.UniqueConstraint(
                fields=('usuario', 'conversacion'),
                name='unique_conversacion_oculta_usuario',
            ),
        ),
    ]
