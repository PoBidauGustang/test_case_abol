#!/bin/bash
export PYTHONPATH=$SRC_PATH
alembic upgrade head
rm poetry.lock
rm pyproject.toml
cd "$APP_DIR" || exit
rm Dockerfile
gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind "$API_HOST":"$API_PORT"
