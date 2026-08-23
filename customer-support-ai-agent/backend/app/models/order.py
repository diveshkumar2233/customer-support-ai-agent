"""Order table: mock e-commerce order data the tools operate on."""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.database.connection import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    status = Column(String, default="processing")  # processing|shipped|delivered|cancelled
    total_amount = Column(Float, nullable=False)
    is_cancellable = Column(Boolean, default=True)
    is_refundable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
