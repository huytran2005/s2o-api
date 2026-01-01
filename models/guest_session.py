import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.database import Base


class GuestSession(Base):
    __tablename__ = "guest_session"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    qr_id = Column(
        UUID(as_uuid=True),
        ForeignKey("qr_code.id"),
        nullable=False
    )

    session_token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    qr = relationship("QRCode")
