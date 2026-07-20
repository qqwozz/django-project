#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser..."
python manage.py shell -c "
from users.models import CustomUser
if not CustomUser.objects.filter(email='admin@example.com').exists():
    CustomUser.objects.create_superuser(
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        password='admin12345'
    )
    print('Superuser created: admin@example.com / admin12345')
else:
    print('Superuser already exists')
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec gunicorn enf.wsgi:application --bind 0.0.0.0:8000 --workers 3
