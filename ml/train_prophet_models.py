# --- سكربت تدريب Prophet لكل منتج وتخزين النموذج ---
import os
import pandas as pd
from prophet import Prophet
import joblib
from sqlalchemy import create_engine
from datetime import datetime

# --- إعداد الاتصال بقاعدة البيانات ---
DB_PATH = "sqlite:///bakery.db"  # غيّريه إذا كنتِ تستخدمين قاعدة مختلفة
engine = create_engine(DB_PATH)

# --- إنشاء مجلد لحفظ النماذج إن لم يكن موجودًا ---
os.makedirs("ai_models/prophet", exist_ok=True)

# --- جلب كل معرفات المنتجات ---
products_df = pd.read_sql("SELECT id FROM products", engine)
product_ids = products_df["id"].tolist()

for product_id in product_ids:
    # --- جلب بيانات الطلبات لهذا المنتج ---
    query = f'''
        SELECT order_date AS ds, SUM(quantity) AS y
        FROM orders
        WHERE product_id = {product_id}
        GROUP BY order_date
        ORDER BY ds ASC
    '''
    df = pd.read_sql(query, engine)

    # تخطي المنتج إذا لا توجد بيانات كافية
    if len(df) < 7:
        print(f"📦 المنتج {product_id}: لا توجد بيانات كافية للتدريب")
        continue

    # تحويل التاريخ إلى datetime
    df["ds"] = pd.to_datetime(df["ds"])

    # --- تدريب نموذج Prophet ---
    model = Prophet(daily_seasonality=True)
    model.fit(df)

    # --- حفظ النموذج لهذا المنتج ---
    model_path = f"ai_models/prophet/prophet_product_{product_id}.pkl"
    joblib.dump(model, model_path)
    print(f"✅ تم تدريب وحفظ نموذج المنتج {product_id}")

print("🎉 تم تدريب كل النماذج بنجاح")

