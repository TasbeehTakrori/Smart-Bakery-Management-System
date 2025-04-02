import sqlite3
from datetime import datetime, timedelta
import random

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("bakery.db")
cursor = conn.cursor()

# حذف البيانات السابقة (اختياري)
cursor.execute("DELETE FROM orders")

# إعداد المنتجات
product_ids = [1, 2, 3]
days_back = 30

for product_id in product_ids:
    for i in range(days_back):
        date = (datetime.today() - timedelta(days=i)).date()
        if product_id == 1:
            qty = random.randint(1, 5)  # منتج عادي
        elif product_id == 2:
            qty = random.randint(4, 8)  # منتج عليه طلب أكثر
        else:
            qty = random.randint(1, 2)  # منتج ضعيف المبيعات

        cursor.execute(
            "INSERT INTO orders (product_id, quantity, order_date) VALUES (?, ?, ?)",
            (product_id, qty, date)
        )

conn.commit()
conn.close()

print("✅ تم توليد بيانات وهمية للطلبات لـ 30 يوم")
