## Migrations

py manage.py makemigrations auctions &&
py manage.py migrate auctions &&
py manage.py migrate

## Superuser

py manage.py createsuperuser
py manage.py createsuperuser --username florestan --email florestan@example.com

## Seed the database

Use [django-seed](https://github.com/Brobin/django-seed)

pip3 install django-seed
add "django_seed" to INSTALLED_APPS in seetings.py

py manage.py seed auctions --number=15

OR to seed from `tests.py` file
py manage.py test

## Reset DB

py manage.py flush
