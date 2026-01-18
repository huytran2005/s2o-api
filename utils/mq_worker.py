import json
import pika

from db.database import SessionLocal

from models.order import Order
from models.user import User
import models

from utils.reward import reward_on_order_served
from utils.notification import notify_order_status
from utils.analytics import log_analytics

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
QUEUE_NAME = "order_events"

def handle_event(event: str, payload: dict):
    print("EVENT:", event)
    print("PAYLOAD:", payload)

    db = SessionLocal()
    try:
        # Analytics cho mọi event
        log_analytics(db, event, payload)

        if event == "ORDER_STATUS_UPDATED":
            order = db.query(Order).filter(Order.id == payload["order_id"]).first()
            if not order:
                return

            user = db.query(User).filter(User.id == order.user_id).first() if order.user_id else None

            # Notification (stub)
            if user:
                notify_order_status(user, payload.get("status"))

            # Reward chỉ khi served
            if payload.get("status") == "served" and order.user_id:
                changed = reward_on_order_served(db, order)
                if changed:
                    db.commit()
                    print("REWARD ADDED")
                else:
                    print("REWARD SKIPPED (duplicate)")
    finally:
        db.close()

def start_worker():
    params = pika.URLParameters(RABBITMQ_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE_NAME, durable=True)

    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)
            handle_event(data["event"], data["payload"])
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print("WORKER ERROR:", e)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    ch.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    print("RabbitMQ Worker is running...")
    ch.start_consuming()

if __name__ == "__main__":
    start_worker()
