#!/bin/sh
set -xe

echo "Waiting for mysql..."

while ! nc -z db 3306; do
  sleep 10
done

echo "Mysql started"

python manage.py makemigrations --no-input
python manage.py makemigrations BAapp --no-input
python manage.py migrate --no-input

rm -rf /app/static/*
python manage.py collectstatic --no-input

gunicorn --bind :8000 --workers 3 config.wsgi
