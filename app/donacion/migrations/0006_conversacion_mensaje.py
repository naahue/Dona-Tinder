# Generated manually: Conversacion, Mensaje + backfill from DecisionDonacion (interes)

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_conversaciones(apps, schema_editor):
    DecisionDonacion = apps.get_model('donacion', 'DecisionDonacion')
    Conversacion = apps.get_model('donacion', 'Conversacion')
    interes_valor = 1
    for row in DecisionDonacion.objects.filter(tipo=interes_valor).iterator():
        Conversacion.objects.get_or_create(
            donacion_id=row.donacion_id,
            interesado_id=row.usuario_id,
            defaults={},
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('donacion', '0005_decision_donacion_y_mostrar_en_feed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                (
                    'escritura_bloqueada',
                    models.BooleanField(
                        default=False,
                        help_text='Si es True, no se pueden enviar mensajes (p. ej. donación ya entregada a otro).',
                    ),
                ),
                (
                    'donacion',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='conversaciones',
                        to='donacion.donacion',
                    ),
                ),
                (
                    'interesado',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='conversaciones_como_interesado',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Mensaje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cuerpo', models.TextField(max_length=2000)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                (
                    'autor',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='mensajes_enviados',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'conversacion',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='mensajes',
                        to='donacion.conversacion',
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name='conversacion',
            constraint=models.UniqueConstraint(
                fields=('donacion', 'interesado'),
                name='unique_conversacion_donacion_interesado',
            ),
        ),
        migrations.RunPython(backfill_conversaciones, noop),
    ]
