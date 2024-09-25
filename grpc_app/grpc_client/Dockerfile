FROM python:3.12-slim

RUN pip install Flask grpcio grpcio-tools python-dotenv
RUN apt-get update && apt-get install -y iputils-ping
COPY . /app

WORKDIR /app

CMD ["python", "-u", "grpc_client.py"]
