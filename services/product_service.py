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
