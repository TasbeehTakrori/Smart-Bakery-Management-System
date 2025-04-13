from models.base import Base
from models.product import Product
from models.order import Order
from models.raw_material import RawMaterial
from models.product_ingredient import ProductIngredient
from config import engine  # تأكدي أن هذا المسار صحيح

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ تم إنشاء الجداول.")
