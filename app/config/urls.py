"""URL principal del proyecto (paquete `config`)."""

import re
from urllib.parse import urlsplit

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from config.health import health

urlpatterns = [
    path('health/', health, name='health'),
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls', namespace='usuarios')),
    path('', include('donacion.urls', namespace='donacion')),
    path('accounts/', include('django.contrib.auth.urls')),
]

# static() solo registra rutas si DEBUG=True; con DJANGO_DEBUG=false y DJANGO_SERVE_MEDIA=true
# (p. ej. Docker) hay que servir MEDIA con re_path + serve.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif settings.SERVE_MEDIA:
    _prefix = settings.MEDIA_URL
    if _prefix and not urlsplit(_prefix).netloc:
        urlpatterns += [
            re_path(
                r'^%s(?P<path>.*)$' % re.escape(_prefix.lstrip('/')),
                serve,
                kwargs={'document_root': settings.MEDIA_ROOT},
            ),
        ]
