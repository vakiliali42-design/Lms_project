#!/bin/sh

echo "Waiting for database..."

# (اختیاری) صبر برای بالا آمدن دیتابیس
sleep 5

echo "Apply migrations..."
python manage.py migrate

echo "Collect static..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"