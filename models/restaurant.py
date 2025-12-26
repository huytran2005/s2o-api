import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from db.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String(255),
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("app_user.id"),
        nullable=False
    )

    # ✅ CHỈ 1 ẢNH PREVIEW
    image_preview = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
