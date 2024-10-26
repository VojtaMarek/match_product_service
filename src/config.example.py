# config example
from typing import Final
import os

# API
AUTH_TOKEN = {"Auth": ""}

# New DB with products
DB_URL = "sqlite:///products.db"

# RabbitMQ connection
rabbitmq_host: Final[str] = os.getenv('RABBITMQ_HOST', '')  # Make sure 'rabbitmq' matches the service name in Docker
rabbitmq_port: Final[str] = os.getenv('RABBITMQ_PORT', '')
rabbitmq_virtual_host: Final[str] = os.getenv('RABBITMQ_VIRTUAL_HOST', '/')
rabbitmq_login: Final[str] = os.getenv('RABBITMQ_LOGIN', '')
rabbitmq_password: Final[str] = os.getenv('RABBITMQ_PASSWORD', '')
RABBITMQ_URL = f'amqp://{rabbitmq_login}:{rabbitmq_password}@{rabbitmq_host}:{rabbitmq_port}/{rabbitmq_virtual_host}'
