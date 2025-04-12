import streamlit
from models.product import Product
from config import SessionLocal

def get_products():
    session = SessionLocal()
    products = session.query(Product).all()
    session.close()

    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "stock": p.stock,
            "image_url": p.image_url,
            "created_at": p.created_at
        }
        for p in products
    ]

def add_product(product):
    session = SessionLocal()
    new_product = Product(
        name=product["name"],
        description=product["description"],
        price=product["price"],
        stock=product["stock"],
        image_url=product.get("image_url"),
        created_at= product.get("created_at")
    )
    session.add(new_product)
    session.commit()
    session.close()

def update_product(product_id, updated_data):
    session = SessionLocal()
    product = session.query(Product).filter(Product.id == product_id).first()

    if product:
        if "name" in updated_data and updated_data["name"] != product.name:
            product.name = updated_data["name"]

        if "description" in updated_data and updated_data["description"] != product.description:
            product.description = updated_data["description"]

        if "price" in updated_data and updated_data["price"] != product.price:
            product.price = updated_data["price"]

        if "stock" in updated_data and updated_data["stock"] != product.stock:
            product.stock = updated_data["stock"]

        if "image_url" in updated_data and updated_data["image_url"] != product.image_url:
            product.image_url = updated_data["image_url"]

        session.commit()

    session.close()

def delete_all_products():
    session = SessionLocal()
    session.query(Product).delete()  # حذف كل الصفوف
    session.commit()
    session.close()

def delete_product(product_id):
    session = SessionLocal()
    product = session.query(Product).filter(Product.id == product_id).first()

    if product:
        session.delete(product)
        session.commit()

    session.close()

def get_product_by_name(name):
    session = SessionLocal()
    product = session.query(Product).filter(Product.name == name).first()  # البحث عن المنتج بالاسم
    return product  # إرجاع المنتج إذا وجد، أو None إذا لم يجد

from models.raw_material import RawMaterial
from sqlalchemy.orm import Session

# دالة لاسترجاع المواد الخام من قاعدة البيانات
def get_raw_materials():
    session = SessionLocal()  # تأكد من أنك قمت بتعريف SessionLocal في config.py أو مكان آخر
    raw_materials = session.query(RawMaterial).all()
    session.close()
    return raw_materials


# دالة للحصول على الـ product_id بناءً على اسم المنتج
def get_product_id_by_name(name):
    session = SessionLocal()

    product = session.query(Product).filter(Product.name == name).first()
    if product:
        return product.id
    return None  # إذا لم يتم العثور على المنتج

from sqlalchemy.orm import Session
from models import ProductIngredient, RawMaterial

def add_product_ingredient(product_id, material, quantity):
    session = SessionLocal()

    # الحصول على الكائنات ذات الصلة من قاعدة البيانات
    product = session.query(Product).filter(Product.id == product_id).first()
    raw_material = session.query(RawMaterial).filter(RawMaterial.name == material).first()

    if product and raw_material:
        # إضافة البيانات إلى جدول المواد الخام المرتبطة بالمنتج
        product_ingredient = ProductIngredient(
            product_id=product.id,
            raw_material_id=raw_material.id,
            quantity_needed=quantity
        )

        # إضافة التغييرات إلى الجلسة
        session.add(product_ingredient)
        session.commit()

        # إغلاق الجلسة
        session.close()

        # تأكيد إضافتها
        return True
    else:
        # في حال عدم العثور على المنتج أو المادة الخام
        session.close()
        return False


def remove_all_raw_materials_for_product(product_id):
    session = SessionLocal()  # افتراض وجود جلسة SQLAlchemy
    session.query(ProductIngredient).filter(ProductIngredient.product_id == product_id).delete()
    session.commit()
    print(f"تم حذف المواد الخام المرتبطة بالمنتج {product_id}")