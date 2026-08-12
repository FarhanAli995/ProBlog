#!/bin/sh
set -e

echo "Waiting is not needed for sqlite, applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting: $@"
exec "$@"
