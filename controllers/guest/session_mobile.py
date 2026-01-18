# controllers/guest/session_mobile.py

import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.qr_code import QRCode
from models.guest_session import GuestSession

router = APIRouter(prefix="/guest/session", tags=["Guest Mobile"])


@router.post("/mobile")
def create_guest_session_mobile(
    code: str,
    db: Session = Depends(get_db),
):
    qr = (
        db.query(QRCode)
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
        "expires_at": session.expires_at,
        "table_id": qr.table_id,
        "restaurant_id": qr.restaurant_id,
    }
