from fastapi import APIRouter
from sqlalchemy import text
from db.database import SessionLocal
import pika
import os

router = APIRouter()


@router.get("/health")
def health_check():
    result = {
        "status": "ok",
        "db": "ok",
        "rabbitmq": "ok",
    }

    # --- DB check ---
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
    except Exception:
        result["status"] = "error"
        result["db"] = "error"
    finally:
        db.close()

    # --- RabbitMQ check ---
    try:
        params = pika.URLParameters(os.getenv("RABBITMQ_URL"))
        connection = pika.BlockingConnection(params)
        connection.close()
    except Exception:
        result["status"] = "error"
        result["rabbitmq"] = "error"

    return result