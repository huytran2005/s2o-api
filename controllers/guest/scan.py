from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.qr_code import QRCode

router = APIRouter(prefix="/guest", tags=["Guest"])


@router.get("/scan")
def scan_qr(code: str, db: Session = Depends(get_db)):
    qr = (
        db.query(QRCode)
        .filter(QRCode.code == code, QRCode.status == "active")
        .first()
    )

    if not qr:
        raise HTTPException(status_code=404, detail="Invalid QR")

    return {
        "qr_code": qr.code,
        "table_id": qr.table_id,
        "restaurant_id": qr.restaurant_id,
    }
