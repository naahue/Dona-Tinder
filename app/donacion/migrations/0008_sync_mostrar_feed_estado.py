# Alinea mostrar_en_feed con estado_publicacion y retirado

from django.db import migrations


def sync_mostrar_feed(apps, schema_editor):
    Donacion = apps.get_model('donacion', 'Donacion')
    activa = 1
    for d in Donacion.objects.iterator():
        mostrar = d.estado_publicacion == activa and not d.retirado
        if d.mostrar_en_feed != mostrar:
            Donacion.objects.filter(pk=d.pk).update(mostrar_en_feed=mostrar)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('donacion', '0007_donacion_estado_publicacion'),
    ]

    operations = [
        migrations.RunPython(sync_mostrar_feed, noop),
    ]
