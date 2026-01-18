from fastapi import APIRouter, Depends
from utils.dependencies import get_guest_session_mobile

router = APIRouter(prefix="/guest", tags=["Guest Mobile"])

@router.get("/me-mobile")
def me_mobile(session = Depends(get_guest_session_mobile)):
    return {
        "message": "Mobile session OK",
        "qr_id": str(session.qr_id),
        "expires_at": session.expires_at,
    }
