# DONA-Tinder

Proyecto Django + PostgreSQL. Trabajá siempre desde la carpeta donde está [`docker-compose.yml`](docker-compose.yml).

## Primera vez

Creá **`.env`** al lado del compose con **`DJANGO_SECRET_KEY=`** (valor largo y aleatorio). Guía de variables: [`app/env.sample`](app/env.sample).

## Comandos (los únicos que necesitás día a día)

```text
docker compose up -d
```

```text
docker compose down -v
```

**`down -v`** borra la base y los archivos que estaban guardados como media **dentro de Docker** (`postgres_data` + `uploads_data`). Después tocás **`up -d`** otra vez y el contenedor corre migraciones y el seed demo (salvo que desactives el seed en el compose).

Opcional cuando depurás: **`docker compose logs -f web`**.

## Demo en el navegador

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

Las fotos de ejemplo están en [`app/donacion/fixtures/seed_demo/`](app/donacion/fixtures/seed_demo/) dentro del código; **`down -v`** no borra esa carpeta.

| Rol | Correo | Contraseña |
|-----|--------|------------|
| Admin | `admin@dt.com` | `admin123` |
| Donador | `dona@dt.com` | `Dona.2026` |
| Interesado | `inte@dt.com` | `Dona.2026` |

## Resto

- Producción más adelante: ver comentarios en [`docker-compose.yml`](docker-compose.yml).
- Scripts en **`bin/`** (p. ej. [`bin/clean_local_artifacts`](bin/)): solo ayudas si desarrollás con archivos locales bajo **`app/`** fuera del flujo Compose; **`docker compose` no los ejecuta.**
- **Reset rápido** encadenando los mismos comandos: [`restart-demo.cmd`](restart-demo.cmd) o [`restart-demo.sh`](restart-demo.sh).
- Preferí **`venv`** en **`.venv`**, no en la raíz del repo.

## License

Copyright © 2026 Nahuel Ignacio Soler. All rights reserved. This code is proprietary; no license is granted for use, copying, or distribution without written permission. See [LICENSE](LICENSE).
