#!/bin/sh

# Wait for database to be ready
until PGPASSWORD=$DB_PASSWORD psql -h "db" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# Run migrations
RUN python manage.py makemigrations
RUN python manage.py migrate

# Start Gunicorn
exec gunicorn project.wsgi:application --bind 0.0.0.0:8000