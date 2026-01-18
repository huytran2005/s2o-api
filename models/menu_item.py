from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from db.database import Base
class MenuItem(Base):
    __tablename__ = "menu_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), nullable=False)

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("menu_category.id"),  # ✅ ĐÚNG TÊN BẢNG
        nullable=False
    )

    category = relationship("Category", back_populates="menu_items")

    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Numeric, nullable=False)

    is_available = Column(Boolean, default=True)
    image_url = Column(String)
    meta = Column(JSONB)
