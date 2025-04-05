import sqlite3
from datetime import datetime, timedelta
import random

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("../bakery.db")
cursor = conn.cursor()

# إعداد
product_ids = [1, 2, 3]
days_back = 30
today = datetime.today().date()

# تفريغ الجداول القديمة
cursor.execute("DELETE FROM checkpoint_conditions")
cursor.execute("DELETE FROM orders")

# إنشاء بيانات
for i in range(days_back):
    current_date = today - timedelta(days=i)

    # 1. إنشاء حالة الحواجز
    # نختار 0 أو 1 أو 2، 2 تعني سالك، 0 تعني مغلق
    cp_1 = random.choices([0, 1, 2], weights=[1, 2, 7])[0]
    cp_2 = random.choices([0, 1, 2], weights=[1, 3, 6])[0]
    cp_3 = random.choices([0, 1, 2], weights=[2, 3, 5])[0]
    cp_4 = random.choices([0, 1, 2], weights=[1, 2, 7])[0]
    cp_5 = random.choices([0, 1, 2], weights=[1, 2, 7])[0]

    # إضافة سجل الحواجز
    cursor.execute("""
        INSERT INTO checkpoint_conditions (date, cp_1, cp_2, cp_3, cp_4, cp_5)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (current_date, cp_1, cp_2, cp_3, cp_4, cp_5))

    # نحسب مدى سهولة المرور بناءً على مجموع الحواجز (كلما زادت القيمة، كان المرور أسهل)
    checkpoint_score = cp_1 + cp_2 + cp_3 + cp_4 + cp_5  # من 0 إلى 10

    for product_id in product_ids:
        # قاعدة منطقية:
        # - كلما زاد checkpoint_score زادت فرصة الشراء
        # - كل منتج له متوسط مبيعات مختلف
        if product_id == 1:
            base = 3
        elif product_id == 2:
            base = 5
        else:
            base = 1

        # نحسب الطلب بشكل منطقي: كل نقطة في checkpoint_score تزيد المبيعات
        qty = max(0, int(base + (checkpoint_score - 5) * 0.7 + random.randint(-1, 1)))

        cursor.execute("""
            INSERT INTO orders (product_id, quantity, order_date)
            VALUES (?, ?, ?)
        """, (product_id, qty, current_date))

# حفظ وإغلاق
conn.commit()
conn.close()

print("✅ تم توليد بيانات الطلبات والحواجز بنجاح ✅")

# import sqlite3
# from datetime import datetime, timedelta
# import random
#
# # الاتصال بقاعدة البيانات
# conn = sqlite3.connect("../bakery.db")
# cursor = conn.cursor()
#
#
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS checkpoint_conditions (
#         date TEXT PRIMARY KEY,
#         cp_1 INTEGER,
#         cp_2 INTEGER,
#         cp_3 INTEGER,
#         cp_4 INTEGER,
#         cp_5 INTEGER
#     )
# ''')
#
# # حذف البيانات السابقة (اختياري)
# cursor.execute("DELETE FROM checkpoint_conditions")
#
#
# # توليد التواريخ
# days_back = 90
# for i in range(days_back + 5):  # +1 لليوم الحالي
#     date = (datetime.today() - timedelta(days=i)).date()
#
#     # توليد حالة عشوائية لكل حاجز (0 = مغلق، 1 = مزدحم، 2 = مفتوح)
#     cp_1 = random.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]
#     cp_2 = random.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]
#     cp_3 = random.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]
#     cp_4 = random.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]
#     cp_5 = random.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]
#
#     # إدخال الصف
#     cursor.execute(
#         '''
#         INSERT INTO checkpoint_conditions (date, cp_1, cp_2, cp_3, cp_4, cp_5)
#         VALUES (?, ?, ?, ?, ?, ?)
#         ''',
#         (date.isoformat(), cp_1, cp_2, cp_3, cp_4, cp_5)
#     )
#
# conn.commit()
# conn.close()
#
# print("✅ تم توليد بيانات الحواجز لمدة 90 يوم بنجاح.")