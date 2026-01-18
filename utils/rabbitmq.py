import os
import pika
import json

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://guest:guest@rabbitmq:5672/"
)

def publish_event(event_type: str, payload: dict):
    """
    Gửi 1 event vào RabbitMQ
    """
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue="order_events", durable=True)

    message = {
        "event": event_type,
        "payload": payload
    }

    channel.basic_publish(
        exchange="",
        routing_key="order_events",
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    connection.close()
