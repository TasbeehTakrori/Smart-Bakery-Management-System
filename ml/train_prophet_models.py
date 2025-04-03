import os
import pandas as pd
from prophet import Prophet
import joblib
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from services.weather_service import get_historical_weather_data  # استيراد دالة جلب الطقس
import streamlit as st

# إعداد الاتصال بقاعدة البيانات
DB_PATH = "sqlite:///bakery.db"  # غيّريه إذا كنتِ تستخدمين قاعدة بيانات مختلفة
engine = create_engine(DB_PATH)

# إنشاء مجلد لحفظ النماذج إن لم يكن موجودًا
os.makedirs("ai_models/prophet", exist_ok=True)


# دالة تدريب النماذج
def retrain_prophet_models_with_weather():
    products_df = pd.read_sql("SELECT id FROM products", engine)
    product_ids = products_df["id"].tolist()

    total_products = len(product_ids)

    # شريط التقدم
    st.session_state.retraining_in_progress = True  # تحديث الحالة في الجلسة
    progress_bar = st.progress(0)

    for idx, product_id in enumerate(product_ids):
        query = f'''
            SELECT order_date AS ds, SUM(quantity) AS y
            FROM orders
            WHERE product_id = {product_id}
            GROUP BY order_date
            ORDER BY ds ASC
        '''
        df = pd.read_sql(query, engine)

        if len(df) < 7:
            continue

        # جلب بيانات الطقس (نفترض هنا أن الطقس متاح عبر جميع الأيام في البيانات)
        weather_data = get_historical_weather_data(df["ds"].min(), df["ds"].max())
        weather_df = pd.DataFrame(weather_data)

        # دمج بيانات الطقس مع بيانات الطلب
        df = df.merge(weather_df, on="ds", how="left")

        # تدريب نموذج Prophet
        model = Prophet(daily_seasonality=True)
        model.add_regressor("temperature")
        model.add_regressor("humidity")
        model.add_regressor("wind_speed")
        model.fit(df)

        model_path = f"ai_models/prophet/prophet_product_{product_id}.pkl"
        joblib.dump(model, model_path)

        # تحديث التقدم
        progress = int(((idx + 1) / total_products) * 100)
        progress_bar.progress(progress)

    st.session_state.retraining_in_progress = False  # إيقاف حالة التدريب عند الانتهاء

    return "🎉 تم تدريب كل النماذج بنجاح"