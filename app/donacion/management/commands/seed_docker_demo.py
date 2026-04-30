import os
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from donacion.models import Conversacion, DecisionDonacion, Donacion, Mensaje

DEMO_DONADOR_EMAIL = 'dona@dt.com'
DEMO_INTERESADO_EMAIL = 'inte@dt.com'
DEMO_PASSWORD = 'Dona.2026'
DEMO_ADMIN_EMAIL = 'admin@dt.com'
DEMO_ADMIN_PASSWORD = 'admin123'


def _load_fixture_image(filename: str) -> ContentFile:
    path = Path(settings.BASE_DIR) / 'donacion' / 'fixtures' / 'seed_demo' / filename
    if not path.is_file():
        raise CommandError('No se encuentra fixture de demo: %s' % path)
    return ContentFile(path.read_bytes(), name=filename)


class Command(BaseCommand):
    help = 'Carga usuarios y donaciones de demostración (fotos en donacion/fixtures/seed_demo/). Idempotente.'

    def handle(self, *args, **options):
        if os.environ.get('SKIP_DOCKER_DEMO_SEED', '').strip().lower() in ('1', 'true', 'yes'):
            self.stdout.write('Omitiendo seed (SKIP_DOCKER_DEMO_SEED).')
            return

        User = get_user_model()

        if not User.objects.filter(email=DEMO_ADMIN_EMAIL).exists():
            User.objects.create_superuser(
                email=DEMO_ADMIN_EMAIL,
                password=DEMO_ADMIN_PASSWORD,
                first_name='Admin',
                last_name='DT',
            )
            self.stdout.write('Creado superusuario %(e)s.' % {'e': DEMO_ADMIN_EMAIL})

        if User.objects.filter(email=DEMO_DONADOR_EMAIL).exists():
            self.stdout.write('Demo ya cargado (omitir donaciones/usuarios demo).')
            return

        donador = User.objects.create_user(
            email=DEMO_DONADOR_EMAIL,
            password=DEMO_PASSWORD,
            first_name='Donador',
            last_name='DT',
        )
        interesado = User.objects.create_user(
            email=DEMO_INTERESADO_EMAIL,
            password=DEMO_PASSWORD,
            first_name='Interesado',
            last_name='DT',
        )

        muestrario = (
            (
                'Bañera rectangular',
                2,
                'Bañera blanca buen estado, toalla de presentación incluida. Baño en tonos beige. Coordinar retiro.',
                'banera.png',
            ),
            (
                'Cama matrimonial',
                2,
                'Dormitorio con cama vestida, mesas de luz y vista alta a la ciudad. Coordinar día y forma de retiro.',
                'cama_ambiente.png',
            ),
            (
                'Smart TV LG',
                2,
                'Televisor LG de pantalla plana funcionando, sobre mueble blanco. Dos controles.',
                'tv_smart.png',
            ),
        )
        donaciones_guardadas = []
        for idx, (nombre, estado_obj, descr, foto) in enumerate(muestrario):
            don = Donacion(
                nombre=nombre,
                estado=estado_obj,
                descripcion=descr[:200],
                donador=donador,
                retirado=False,
                mostrar_en_feed=True,
                estado_publicacion=Donacion.EstadoPublicacion.ACTIVA,
            )
            cf = _load_fixture_image(foto)
            ext = Path(foto).suffix.lower() or '.png'
            don.imagen.save('seed_demo_%s%s' % (idx, ext), cf, save=False)
            don.save()
            donaciones_guardadas.append(don)

        d0 = donaciones_guardadas[0]
        DecisionDonacion.objects.create(usuario=interesado, donacion=d0, tipo=DecisionDonacion.Tipo.INTERES)
        conv, _ = Conversacion.objects.get_or_create(donacion=d0, interesado=interesado)
        Mensaje.objects.create(conversacion=conv, autor=interesado, cuerpo='¿Sigue disponible la bañera?')
        Mensaje.objects.create(conversacion=conv, autor=donador, cuerpo='Sí, coordinamos cuando quieras.')

        self.stdout.write(
            self.style.SUCCESS(
                'Demo listo:\n'
                '  Admin Django: %(adm)s / %(admp)s\n'
                '  %(a)s / %(p)s\n'
                '  %(b)s / %(p)s\n'
                'El interesado ya marcó “me interesa” en “%(n)s”; hay mensajes en el chat.'
                % {
                    'a': DEMO_DONADOR_EMAIL,
                    'b': DEMO_INTERESADO_EMAIL,
                    'p': DEMO_PASSWORD,
                    'n': d0.nombre,
                    'adm': DEMO_ADMIN_EMAIL,
                    'admp': DEMO_ADMIN_PASSWORD,
                }
            )
        )
