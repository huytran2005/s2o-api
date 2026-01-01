from pydantic import BaseModel
from uuid import UUID


class QRCreateResponse(BaseModel):
    qr_id: UUID
    code: str
class QRScanResponse(BaseModel):
    session_token: str

    restaurant: dict
    table: dict | None
