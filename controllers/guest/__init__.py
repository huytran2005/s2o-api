from fastapi import APIRouter

from .scan import router as scan_router
from .session_web import router as session_web_router
from .session_mobile import router as session_mobile_router
from .me import router as me_router
from .me_mobile import router as me_mobile_router
from .qr_entry import router as qr_entry_router
from .guest_qr import router as guest_qr_router
router = APIRouter()
router.include_router(guest_qr_router)
router.include_router(scan_router)
router.include_router(session_web_router)
router.include_router(session_mobile_router)
router.include_router(me_router)
router.include_router(me_mobile_router)
router.include_router(qr_entry_router)
