#!/bin/sh
# Container entrypoint: migrate, then serve. Railway does not run the start
# command through a shell, so any $PORT expansion has to happen in here.
set -e
PORT="${PORT:-8000}"
echo "[start] uid=$(id -u) cwd=$(pwd) port=$PORT"
python manage.py migrate --noinput
echo "[start] migrations done, launching gunicorn on 0.0.0.0:$PORT"
exec gunicorn --bind "0.0.0.0:$PORT" --workers 2 --threads 4 --worker-class gthread \
  --timeout 120 --log-level info --access-logfile - --error-logfile - \
  backend.wsgi:application
