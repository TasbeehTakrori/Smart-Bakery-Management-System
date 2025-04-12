from models.raw_material import RawMaterial
from services.product_ai import predict_daily_demand_with_weather
from models.product_ingredient import ProductIngredient
from sqlalchemy.orm import joinedload
from config import SessionLocal
from models import RawMaterial, ProductIngredient, Product


def get_raw_material_demand():
    session = SessionLocal()
    try:
        # جلب المواد الخام
        raw_materials = session.query(RawMaterial).all()

        # جلب التوقعات اليومية للمنتجات مرة واحدة
        product_demand = {}
        products = session.query(Product).all()
        for product in products:
            product_demand[product.id] = predict_daily_demand_with_weather(product.id)
            print(f"product_demand: {product.name}, {product_demand[product.id]}")
        raw_material_demand = {}

        for material in raw_materials:
            total_demand = 0

            # جلب المنتجات التي تحتاج إلى المادة الخام
            product_ingredients = session.query(ProductIngredient).filter(
                ProductIngredient.raw_material_id == material.id).all()

            for product_ingredient in product_ingredients:
                product_id = product_ingredient.product_id
                quantity_needed = product_ingredient.quantity_needed

                # استخدام التوقع اليومي للمنتج
                demand = product_demand[product_id]

                # حساب الكمية المطلوبة من المادة الخام بناءً على الطلب
                total_demand += (demand * quantity_needed)

            raw_material_demand[material.name] = total_demand

        return raw_material_demand

    except Exception as e:
        print(f"Error: {e}")
        return {}
    finally:
        session.close()


#
# def get_raw_material_demand():
#     session = SessionLocal()
#     try:
#         raw_materials = session.query(RawMaterial).all()  # استرجاع جميع المواد الخام
#         raw_material_demand = {}
#
#         for material in raw_materials:
#             print(f"material: {material.name}")
#             # استخراج جميع المنتجات التي تستخدم المادة الخام
#             product_ingredients = session.query(ProductIngredient).filter(ProductIngredient.raw_material_id == material.id).all()
#
#             total_demand = 0
#
#             # حساب الطلب المتوقع لكل منتج يستخدم هذه المادة الخام
#             for product_ingredient in product_ingredients:
#                 print(f"p: {product_ingredient.quantity_needed}")
#
#                 product_id = product_ingredient.product_id
#                 # جلب الطلب المتوقع للمنتج باستخدام نموذج Prophet أو أي طريقة أخرى
#                 demand = predict_daily_demand_with_weather(product_id)
#                 total_demand += demand * product_ingredient.quantity_needed  # الكمية المطلوبة من المادة الخام بناءً على الطلب المتوقع
#
#             raw_material_demand[material.name] = total_demand
#
#         return raw_material_demand
#
#     except Exception as e:
#         print(f"Error: {e}")
#         return {}
#     finally:
#         session.close()

#
# def get_expected_raw_material_quantities():
#     session = SessionLocal()  # فتح جلسة
#     raw_materials = session.query(RawMaterial).all()  # جلب جميع المواد الخام
#     expected_quantities = {}
#
#     for material in raw_materials:
#         # هنا نقوم بحساب الكميات المتوقعة بناءً على المنتجات
#         product_ingredients = session.query(ProductIngredient).filter(
#             ProductIngredient.raw_material_id == material.id).all()
#         total_quantity = 0
#
#         # نقوم بحساب كمية المادة الخام المطلوبة لكل منتج
#         for product_ingredient in product_ingredients:
#             product = product_ingredient.product
#             demand = predict_daily_demand_with_weather(product.id)  # نفترض أنك تستخدم الدالة الخاصة بالتنبؤ
#
#             if demand is not None:  # التأكد من أن القيمة ليست None
#                 total_quantity += product_ingredient.quantity_needed * demand  # احتساب الكمية المتوقعة من المادة الخام
#
#         expected_quantities[material.name] = total_quantity
#         print(f"expected_quantities: {expected_quantities[material.name]} = {total_quantity}")
#
#     session.close()
#     return expected_quantities
#


def add_raw_material(new_raw_material):
    session = SessionLocal()
    try:
        new_raw_material = RawMaterial(
            name=new_raw_material['name'],
            price_per_unit=new_raw_material["price_per_unit"],
            quantity_in_stock=new_raw_material["quantity_in_stock"]
        )
        session.add(new_raw_material)
        session.commit()
        print(f"✅ تم إضافة المادة الخام بنجاح: {new_raw_material['name']}")
    except Exception as e:
        session.rollback()
        print(f"حدث خطأ أثناء إضافة المادة الخام: {e}")
    finally:
        session.close()


# دالة لحذف مادة خام من قاعدة البيانات
def delete_raw_material(raw_material_id):
    session = SessionLocal()
    try:
        # تحقق من وجود المادة الخام في جدول product_ingredients
        product_ingredients = session.query(ProductIngredient).filter(
            ProductIngredient.raw_material_id == raw_material_id).all()

        if product_ingredients:
            # إذا كانت المادة الخام مرتبطة بمنتج، يمكن إما حذف أو تحديث العلاقات أولاً
            for product_ingredient in product_ingredients:
                session.delete(product_ingredient)

        # الآن يمكن حذف المادة الخام
        raw_material = session.query(RawMaterial).filter(RawMaterial.id == raw_material_id).first()

        if raw_material:
            session.delete(raw_material)
            session.commit()
            print(f"✅ تم حذف المادة الخام بنجاح!")
        else:
            print(f"المادة الخام غير موجودة في قاعدة البيانات.")

    except Exception as e:
        session.rollback()
        print(f"حدث خطأ أثناء حذف المادة الخام: {e}")
    finally:
        session.close()


# دالة لاسترجاع المواد الخام من قاعدة البيانات
def get_raw_materials():
    session = SessionLocal()  # تأكد من أنك قمت بتعريف SessionLocal في config.py أو مكان آخر
    raw_materials = session.query(RawMaterial).all()
    session.close()
    return raw_materials


def update_raw_material(raw_material_id, updated_data):
    session = SessionLocal()  # إنشاء جلسة
    try:
        raw_material = session.query(RawMaterial).filter(RawMaterial.id == raw_material_id).first()
        if raw_material:
            # تحديث الحقول بالقيم الجديدة
            raw_material.name = updated_data["name"]
            raw_material.price_per_unit = updated_data["price_per_unit"]
            raw_material.quantity_in_stock = updated_data["quantity_in_stock"]

            session.commit()  # حفظ التغييرات
            return True
        else:
            print("Flase")
            return False  # إذا لم يتم العثور على المادة الخام
    except Exception as e:
        session.rollback()  # التراجع عن التغييرات في حالة حدوث خطأ
        print(f"Error: {e}")
        return False
    finally:
        session.close()  # إغلاق الجلسة بعد التحديث







# دالة لتحويل الكائن إلى قاموس لتمكين العرض بشكل أسهل
def as_dict(self):
    return {
        "id": self.id,
        "name": self.name,
        "price_per_unit": self.price_per_unit,
        "quantity_in_stock": self.quantity_in_stock,
        "created_at": self.created_at,
    }

# إضافة الدالة إلى الفئة RawMaterial
RawMaterial.as_dict = as_dict