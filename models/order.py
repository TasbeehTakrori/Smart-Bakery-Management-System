from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from models.base import Base
from datetime import date

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    order_date = Column(Date, default=date.today)

    product = relationship("Product", back_populates="orders")
