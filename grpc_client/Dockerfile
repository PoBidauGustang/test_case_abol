# Используем базовый образ Python
FROM python:3.12-slim

# Устанавливаем необходимые пакеты
RUN pip install Flask grpcio grpcio-tools
RUN apt-get update && apt-get install -y iputils-ping
# Копируем код Flask клиента
COPY . /app

WORKDIR /app

# Запускаем Flask приложение
CMD ["python", "-u", "grpc_client.py"]
