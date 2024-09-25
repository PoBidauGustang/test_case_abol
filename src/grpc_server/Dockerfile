# Use official Python image as the base image
FROM python:3.12-slim


# Copy the requirements file and install dependencies
RUN pip install grpcio grpcio-tools SQLAlchemy asyncpg faststream aio_pika

# Copy the application code
COPY . /app

WORKDIR /app


# Command to run the gRPC server
CMD ["python", "-u", "grpc_server.py"]
