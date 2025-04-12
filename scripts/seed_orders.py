import sqlite3
from datetime import datetime

# إعداد الاتصال بقاعدة البيانات (تأكد من المسار الصحيح لقاعدة البيانات)
conn = sqlite3.connect("../bakery.db")  # تأكد من المسار الصحيح للقاعدة
cursor = conn.cursor()


# إنشاء بيانات المواد الخام
def seed_raw_materials():
    raw_materials = [
        ("طحين", 5.5, 100),
        ("سكر", 3.0, 150),
        ("زيت نباتي", 10.0, 200),
        ("خميرة", 2.0, 50),
        ("ملح", 1.5, 75)
    ]

    # إفراغ جدول المواد الخام قبل إضافة بيانات جديدة
    cursor.execute("DELETE FROM raw_materials")
    conn.commit()

    # إضافة البيانات الجديدة مع تاريخ الإنشاء
    for material in raw_materials:
        # الحصول على التاريخ الحالي
        created_at = datetime.now()

        # الاستعلام لإدخال البيانات
        query = """
                INSERT INTO raw_materials (name, price_per_unit, quantity_in_stock, created_at)
                VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (material[0], material[1], material[2], created_at))

    # حفظ التغييرات
    conn.commit()
    print("✅ تم إضافة المواد الخام بنجاح!")


# تشغيل عملية الـ seeding
seed_raw_materials()

# إغلاق الاتصال بعد الانتهاء
conn.close()
#########

# import sqlite3
# from datetime import datetime, timedelta
# import random
#
# # الاتصال بقاعدة البيانات
# conn = sqlite3.connect("../bakery.db")
# cursor = conn.cursor()
#
# # إعداد
# product_id = 4
# days_back = 30
# today = datetime.today().date()
#
# for i in range(days_back):
#     current_date = today - timedelta(days=i)
#
#     # جلب حالة الحواجز في هذا اليوم
#     cursor.execute("""
#         SELECT cp_1, cp_2, cp_3, cp_4, cp_5
#         FROM checkpoint_conditions
#         WHERE date = ?
#     """, (current_date,))
#     result = cursor.fetchone()
#
#     # إذا لم تكن هناك بيانات حواجز لهذا اليوم، ننتقل لليوم التالي
#     if not result:
#         continue
#
#     cp_1, cp_2, cp_3, cp_4, cp_5 = result
#     checkpoint_score = cp_1 + cp_2 + cp_3 + cp_4 + cp_5
#
#     # تحديد متوسط الطلب الأساسي للمنتج رقم 4
#     base = 10
#
#     # حساب الكمية المطلوبة بشكل منطقي
#     qty = max(0, int(base + (checkpoint_score - 5) * 0.7 + random.randint(-1, 1)))
#
#     # إدخال الطلب
#     cursor.execute("""
#         INSERT INTO orders (product_id, quantity, order_date)
#         VALUES (?, ?, ?)
#     """, (product_id, qty, current_date))
#
# # حفظ وإغلاق
# conn.commit()
# conn.close()
#
# print("✅ تم إدخال بيانات المنتج رقم 4 بنجاح لمدة 30 يوم ✅")


# import sqlite3
# from datetime import datetime, timedelta
# import random
#
# # الاتصال بقاعدة البيانات
# conn = sqlite3.connect("../bakery.db")
# cursor = conn.cursor()
#
# # حذف البيانات السابقة (اختياري)
# cursor.execute("DELETE FROM orders")
#
# # إعداد المنتجات
# product_ids = [1, 2, 3]
# days_back = 30
#
# for product_id in product_ids:
#     for i in range(days_back):
#         date = (datetime.today() - timedelta(days=i)).date()
#         if product_id == 1:
#             qty = random.randint(1, 5)  # منتج عادي
#         elif product_id == 2:
#             qty = random.randint(4, 8)  # منتج عليه طلب أكثر
#         else:
#             qty = random.randint(1, 2)  # منتج ضعيف المبيعات
#
#         cursor.execute(
#             "INSERT INTO orders (product_id, quantity, order_date) VALUES (?, ?, ?)",
#             (product_id, qty, date)
#         )
#
# conn.commit()
# conn.close()
#
# print("✅ تم توليد بيانات وهمية للطلبات لـ 30 يوم")
