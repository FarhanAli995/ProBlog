#!/bin/bash

echo "Starting Vercel build..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --noinput || echo "Static collection warning"

# Run migrations with more verbose output
echo "Running database migrations..."
python manage.py makemigrations --noinput || echo "Makemigrations warning"
python manage.py migrate --noinput --verbosity=2 || echo "Migration warning"

echo "Build completed!"
