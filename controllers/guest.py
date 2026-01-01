import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from db.database import get_db
from models.qr_code import QRCode
from models.guest_session import GuestSession

router = APIRouter(prefix="/guest", tags=["Guest"])
@router.api_route("/scan", methods=["GET", "POST"])
def scan_qr(code: str, db: Session = Depends(get_db)):
    qr = (
        db.query(QRCode)
        .options(
            joinedload(QRCode.restaurant),
            joinedload(QRCode.table),
        )
        .filter(QRCode.code == code, QRCode.status == "active")
        .first()
    )

    if not qr:
        raise HTTPException(status_code=400, detail="Invalid QR")

    session_token = secrets.token_urlsafe(32)

    session = GuestSession(
        qr_id=qr.id,
        session_token=session_token,
        expires_at=datetime.utcnow() + timedelta(hours=4),
    )
    db.add(session)
    db.commit()

    return {
        "session_token": session_token,
        "qr": {
            "id": qr.id,
            "type": qr.type,
            "image": qr.image_path,
        },
        "restaurant": {
            "id": qr.restaurant.id,
            "name": qr.restaurant.name,
        },
        "table": {
            "id": qr.table.id,
            "name": qr.table.name,
            "seats": qr.table.seats,
        },
    }
