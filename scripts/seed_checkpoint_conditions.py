import sqlite3
from datetime import datetime, timedelta
import random

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("../bakery.db")
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS checkpoint_conditions (
        date TEXT PRIMARY KEY,
        cp_1 INTEGER,
        cp_2 INTEGER,
        cp_3 INTEGER,
        cp_4 INTEGER,
        cp_5 INTEGER
    )
''')

# حذف البيانات السابقة (اختياري)
cursor.execute("DELETE FROM checkpoint_conditions")


# توليد التواريخ
days_back = 90
for i in range(days_back + 5):  # +1 لليوم الحالي
    date = (datetime.today() - timedelta(days=i)).date()

    # توليد حالة عشوائية لكل حاجز (0 = مغلق، 1 = مزدحم، 2 = مفتوح)
    cp_1 = random.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]
    cp_2 = random.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]
    cp_3 = random.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]
    cp_4 = random.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]
    cp_5 = random.choices([0, 1, 2], weights=[0.1, 0.3, 0.6])[0]

    # إدخال الصف
    cursor.execute(
        '''
        INSERT INTO checkpoint_conditions (date, cp_1, cp_2, cp_3, cp_4, cp_5)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (date.isoformat(), cp_1, cp_2, cp_3, cp_4, cp_5)
    )

conn.commit()
conn.close()

print("✅ تم توليد بيانات الحواجز لمدة 90 يوم بنجاح.")