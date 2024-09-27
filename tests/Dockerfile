FROM python:3.12-slim

ENV SRC_PATH '/app'
ENV APP_DIR 'tests'

WORKDIR $SRC_PATH

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# COPY requirements_test.txt .
RUN pip install --no-cache-dir pytest aiohttp sqlalchemy python-multipart werkzeug asyncpg pydantic pydantic-settings pytest-asyncio==0.21.2 redis grpcio grpcio-tools


COPY ./${APP_DIR} ./${APP_DIR}

RUN chmod +x ${APP_DIR}/entrypoint.sh

ENTRYPOINT ["/bin/bash", "-c", "exec ${SRC_PATH}/${APP_DIR}/entrypoint.sh"]
