# Generated manually for DecisionDonacion and Donacion.mostrar_en_feed

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('donacion', '0004_donacion_retirado'),
    ]

    operations = [
        migrations.AddField(
            model_name='donacion',
            name='mostrar_en_feed',
            field=models.BooleanField(
                default=True,
                help_text='Si está en False, la donación no aparece en el feed de otros (p. ej. reservada).',
            ),
        ),
        migrations.CreateModel(
            name='DecisionDonacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.IntegerField(choices=[(1, 'Interesado'), (2, 'No me interesa')])),
                ('creado', models.DateTimeField(auto_now_add=True)),
                (
                    'donacion',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='decisiones',
                        to='donacion.donacion',
                    ),
                ),
                (
                    'usuario',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='decisiones_donacion',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name='decisiondonacion',
            constraint=models.UniqueConstraint(
                fields=('usuario', 'donacion'),
                name='unique_decision_usuario_donacion',
            ),
        ),
    ]
