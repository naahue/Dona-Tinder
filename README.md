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

[http://127.0.0.1:8000/](http://127.0.0.1:8000/) · panel admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

Las fotos de ejemplo están en [`app/donacion/fixtures/seed_demo/`](app/donacion/fixtures/seed_demo/) dentro del código; **`down -v`** no borra esa carpeta.

| Rol | Correo | Contraseña |
|-----|--------|------------|
| Admin Django | `admin@dt.com` | `admin123` |
| Con donaciones de ejemplo | `dona@dt.com`, `maria@dt.com`, `pedro@dt.com` | `Dona.2026` |
| Sin donaciones (solo cuenta) | `solo@dt.com` | `Dona.2026` |

El seed crea **6 donaciones** de ejemplo (nombres de una palabra), todas activas en el feed (**sin** reservadas, entregadas ni `reservado_con`), **sin** likes ni chats.

## Resto

- Producción más adelante: ver comentarios en [`docker-compose.yml`](docker-compose.yml).
- Preferí **`venv`** en **`.venv`**, no en la raíz del repo.

## License

Copyright © 2026 Nahuel Ignacio Soler. All rights reserved. This code is proprietary; no license is granted for use, copying, or distribution without written permission. See [LICENSE](LICENSE).
