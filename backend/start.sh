#!/bin/sh
# Container entrypoint: migrate, then serve. Railway does not run the start
# command through a shell, so any $PORT expansion has to happen in here.
set -e
PORT="${PORT:-8000}"
echo "[start] uid=$(id -u) cwd=$(pwd) port=$PORT"
python manage.py migrate --noinput

# Railway injects PORT (used by its health check) while the public domain can
# route to a different target port (8000 on this service). Listen on both.
EXTRA_BIND=""
if [ "$PORT" != "8000" ]; then
  EXTRA_BIND="--bind 0.0.0.0:8000"
fi
echo "[start] migrations done, launching gunicorn on 0.0.0.0:$PORT ${EXTRA_BIND:+and 0.0.0.0:8000}"
exec gunicorn --bind "0.0.0.0:$PORT" $EXTRA_BIND --workers 2 --threads 4 --worker-class gthread \
  --timeout 120 --log-level info --access-logfile - --error-logfile - \
  backend.wsgi:application
