import uuid
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base
from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from db.database import Base
from models.restaurant_table import RestaurantTable

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), nullable=False)

    table_id = Column(
        UUID(as_uuid=True),
        ForeignKey("restaurant_table.id"),
        nullable=False
    )

    qr_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)

    status = Column(String, default="pending")
    total_amount = Column(Numeric, default=0)
    currency = Column(String, default="VND")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 👇 ĐỔI TÊN RELATIONSHIP
    table = relationship("RestaurantTable")

    lines = relationship(
        "OrderLine",
        back_populates="order",
        cascade="all, delete"
    )
