# DonaTinder

1. `cd Donatinder`
2. `python -m pip install -r requirements.txt` (o `py -3 -m pip install -r requirements.txt`)
3. `python manage.py migrate`
4. `python manage.py createsuperuser` (opcional: acceso a `/admin/`; mismo intérprete que en el paso 2, p. ej. `py -3`)
5. `python manage.py runserver`
6. Abrí la app en [http://127.0.0.1:8000/](http://127.0.0.1:8000/) y el admin en [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
