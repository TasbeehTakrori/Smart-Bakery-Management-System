from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import Base

class ProductIngredient(Base):
    __tablename__ = 'product_ingredients'
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    raw_material_id = Column(Integer, ForeignKey('raw_materials.id'), primary_key=True)
    quantity_needed = Column(Float)  # كمية المادة الخام المطلوبة

    product = relationship("Product", back_populates="ingredients")
    raw_material = relationship("RawMaterial", back_populates="product_ingredients")

