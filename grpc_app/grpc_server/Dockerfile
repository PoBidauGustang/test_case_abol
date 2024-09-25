FROM python:3.12-slim

RUN pip install grpcio grpcio-tools SQLAlchemy asyncpg faststream aio_pika python-dotenv

COPY . /app

WORKDIR /app

CMD ["python", "-u", "grpc_server.py"]
