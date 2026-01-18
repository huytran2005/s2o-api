from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

router = APIRouter()

HTML_PATH = Path(__file__).parent / "guest_qr.html"


@router.get("/qr-entry", response_class=HTMLResponse)
def qr_entry(
    code: str = Query(..., description="QR code UUID")
):
    """
    Entry point cho QR scan.
    - Mở app bằng intent (Android)
    - Fallback sang web nếu không có app
    """

    if not HTML_PATH.exists():
        return HTMLResponse(
            content="guest_qr.html not found",
            status_code=500,
        )

    html = HTML_PATH.read_text(encoding="utf-8")

    web_base_url = os.getenv("WEB_BASE_URL", "")
    html = html.replace("__WEB_BASE_URL__", web_base_url)

    return HTMLResponse(
        content=html,
        status_code=200,
    )
