from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from models.base import Base

class RawMaterial(Base):
    __tablename__ = 'raw_materials'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price_per_unit = Column(Float)
    quantity_in_stock = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    product_ingredients = relationship("ProductIngredient", back_populates="raw_material")