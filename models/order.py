from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)  # الزبون اختياري
    quantity = Column(Integer)
    order_date = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")