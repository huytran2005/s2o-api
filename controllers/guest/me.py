from fastapi import APIRouter, Depends
from utils.dependencies import get_guest_session

router = APIRouter(prefix="/guest", tags=["Guest"])

@router.get("/me")
def guest_me(session = Depends(get_guest_session)):
    return {
        "message": "Session OK",
        "qr_id": str(session.qr_id),
        "expires_at": session.expires_at,
    }