from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from db.database import get_db
from models.qr_code import QRCode

router = APIRouter(prefix="/qr", tags=["QR"])


@router.get("/entry")
def qr_entry(
    code: str,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. Verify QR tồn tại
    qr = (
        db.query(QRCode)
        .filter(QRCode.code == code, QRCode.status == "active")
        .first()
    )

    if not qr:
        raise HTTPException(status_code=404, detail="Invalid QR")

    ua = request.headers.get("user-agent", "").lower()

    # 2. Android → thử mở app (có fallback web)
    if "android" in ua:
        intent = (
            "intent://qr/open?code=" + code +
            "#Intent;"
            "scheme=s2o;"
            "package=com.example.s2o;"
            "end"
        )
        return RedirectResponse(intent, status_code=302)

    # 3. Fallback mặc định → WEB STATIC
    return RedirectResponse(
        f"http://192.168.88.51:3000/?code={code}",
        status_code=302,
    )
