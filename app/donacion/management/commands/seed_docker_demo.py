import os
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from donacion.models import Donacion

DEMO_PASSWORD = 'Dona.2026'
DEMO_ADMIN_EMAIL = 'admin@dt.com'
DEMO_ADMIN_PASSWORD = 'admin123'


def _load_fixture_image(filename: str) -> ContentFile:
    path = Path(settings.BASE_DIR) / 'donacion' / 'fixtures' / 'seed_demo' / filename
    if not path.is_file():
        raise CommandError('No se encuentra fixture de demo: %s' % path)
    return ContentFile(path.read_bytes(), name=filename)


def _ensure_password(user, pwd: str) -> None:
    if not user.has_usable_password():
        user.set_password(pwd)
        user.save(update_fields=['password'])


def _get_or_create_user(email: str, first_name: str, last_name: str, password: str):
    User = get_user_model()
    u, created = User.objects.get_or_create(
        email=email,
        defaults={'first_name': first_name, 'last_name': last_name},
    )
    if created:
        u.set_password(password)
        u.save()
    else:
        _ensure_password(u, password)
    return u


def _save_imagen_para_donacion(don: Donacion, foto: str, storage_name: str) -> None:
    cf = _load_fixture_image(foto)
    ext = Path(foto).suffix.lower() or '.png'
    don.imagen.save('%s%s' % (storage_name, ext), cf, save=True)


class Command(BaseCommand):
    help = 'Carga usuarios y 6 donaciones demo (una palabra cada una). Idempotente por donador+nombre.'

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

        dona = _get_or_create_user('dona@dt.com', 'Dona', 'Principal', DEMO_PASSWORD)
        maria = _get_or_create_user('maria@dt.com', 'María', 'Donadora', DEMO_PASSWORD)
        pedro = _get_or_create_user('pedro@dt.com', 'Pedro', 'Donador2', DEMO_PASSWORD)
        _get_or_create_user('solo@dt.com', 'Solo', 'Explora', DEMO_PASSWORD)

        def upsert_donacion(
            donador, nombre: str, estado_objetivo: int, descripcion: str, foto: str
        ) -> Donacion:
            nombre_s = nombre.strip()[:20]
            key = 'seed_demo_%s' % nombre_s.lower()
            d = Donacion.objects.filter(donador=donador, nombre=nombre_s).first()
            if d is None:
                d = Donacion(
                    donador=donador,
                    nombre=nombre_s,
                    estado=estado_objetivo,
                    descripcion=descripcion[:200],
                    retirado=False,
                    mostrar_en_feed=True,
                    estado_publicacion=Donacion.EstadoPublicacion.ACTIVA,
                    reservado_con=None,
                )
                d.save()
                created = True
            else:
                d.estado = estado_objetivo
                d.descripcion = descripcion[:200]
                d.retirado = False
                d.estado_publicacion = Donacion.EstadoPublicacion.ACTIVA
                d.reservado_con = None
                d.mostrar_en_feed = True
                d.save()
                created = False
            if created or not d.imagen:
                _save_imagen_para_donacion(d, foto, key)
            return d

        # 6 donaciones: 2 por donador (solo publican dona, maría y pedro).
        demo_filas = [
            (dona, 'Televisor', 2, 'Samsung.', 'televisor.png'),
            (dona, 'Celular', 2, 'Pantalla ok.', 'celular.png'),
            (maria, 'Mesa', 2, 'Madera rústica.', 'mesa.png'),
            (maria, 'Vaso', 1, 'Vidrio.', 'vaso.png'),
            (pedro, 'Silla', 2, 'Asiento gris.', 'silla.png'),
            (pedro, 'Bicicleta', 2, 'Montaña roja.', 'bicicleta.png'),
        ]
        demo_nombres = {nombre for _, nombre, _, _, _ in demo_filas}
        for u in (dona, maria, pedro):
            Donacion.objects.filter(donador=u).exclude(nombre__in=demo_nombres).delete()
        for donador, nombre, est, descr, foto in demo_filas:
            upsert_donacion(donador, nombre, est, descr, foto)

        self.stdout.write(
            self.style.SUCCESS(
                'Seed demo: 6 donaciones (activas).\n'
                '  Admin: %(adm)s / %(admp)s\n'
                '  Misma clave %(pwd)s: dona, maria, pedro, solo.'
                % {'adm': DEMO_ADMIN_EMAIL, 'admp': DEMO_ADMIN_PASSWORD, 'pwd': DEMO_PASSWORD}
            )
        )
