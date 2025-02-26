#!/bin/sh

echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "Database started!"

python manage.py migrate
python manage.py collectstatic --noinput

sleep 10

exec "$@"