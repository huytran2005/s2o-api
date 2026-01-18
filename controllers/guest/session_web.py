import secrets
from datetime import datetime, timedelta
from fastapi import Response, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from db.database import get_db
from models.qr_code import QRCode
from models.guest_session import GuestSession

router = APIRouter(prefix="/guest", tags=["Guest"])

@router.post("/session")
def create_guest_session(
    code: str,
    response: Response,
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

    response.set_cookie(
        key="guest_session",
        value=session_token,
        httponly=True,
        samesite="lax",
        secure=False,   # production: True
        max_age=60 * 60 * 4,
    )

    return {
        "ok": True,
        "session_token": session_token,
        "table_id": qr.table_id,
        "restaurant_id": qr.restaurant_id,
        "expires_at": session.expires_at,
    }

