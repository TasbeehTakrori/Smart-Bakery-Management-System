import os
import pandas as pd
import numpy as np
from prophet import Prophet
import joblib
from sqlalchemy import create_engine
from datetime import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error
from services.weather_service import get_historical_weather_data
import streamlit as st

# الاتصال بقاعدة البيانات
DB_PATH = "sqlite:///bakery.db"
engine = create_engine(DB_PATH)

# التأكد من وجود مجلد لحفظ النماذج
os.makedirs("ai_models/prophet", exist_ok=True)

def retrain_prophet_models_with_weather():
    products_df = pd.read_sql("SELECT id FROM products", engine)
    product_ids = products_df["id"].tolist()
    total_products = len(product_ids)

    st.session_state.retraining_in_progress = True
    progress_bar = st.progress(0)

    for idx, product_id in enumerate(product_ids):
        query = '''
            SELECT order_date AS ds, SUM(quantity) AS y
            FROM orders
            WHERE product_id = :product_id
            GROUP BY order_date
            ORDER BY ds ASC
        '''
        df = pd.read_sql(query, engine, params={"product_id": product_id})

        if len(df) < 7:
            continue

        df["ds"] = pd.to_datetime(df["ds"], errors="coerce", format="mixed").dt.normalize()

        # تحميل بيانات الطقس
        weather_data = get_historical_weather_data(df["ds"].min(), df["ds"].max())
        weather_df = pd.DataFrame(weather_data)
        if weather_df.empty or "ds" not in weather_df.columns:
            continue

        # تحميل بيانات الحواجز من قاعدة البيانات
        checkpoints_query = '''
            SELECT date AS ds, cp_1, cp_2, cp_3, cp_4, cp_5
            FROM checkpoint_conditions
            WHERE ds BETWEEN :start_date AND :end_date
        '''
        checkpoints_df = pd.read_sql(checkpoints_query, engine, params={
            "start_date": df["ds"].min().date().isoformat(),
            "end_date": df["ds"].max().date().isoformat()
        })
        checkpoints_df["ds"] = pd.to_datetime(checkpoints_df["ds"])

        df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
        weather_df["ds"] = pd.to_datetime(weather_df["ds"], errors="coerce")
        checkpoints_df["ds"] = pd.to_datetime(checkpoints_df["ds"], errors="coerce")
        # دمج كل البيانات
        df = df.merge(weather_df, on="ds", how="left")
        df = df.merge(checkpoints_df, on="ds", how="left")

        print(df)
        # التأكد من توفر الأعمدة المطلوبة
        required_columns = ["temperature", "humidity", "wind_speed",
                            "cp_1", "cp_2", "cp_3", "cp_4", "cp_5"]
        if not all(col in df.columns for col in required_columns):
            continue

        # تقسيم البيانات إلى تدريب واختبار
        train_size = int(len(df) * 0.8)
        train_df = df.iloc[:train_size]
        test_df = df.iloc[train_size:]

        # بناء النموذج
        model = Prophet(daily_seasonality=True)
        model.add_regressor("temperature")
        model.add_regressor("humidity")
        model.add_regressor("wind_speed")
        model.add_regressor("cp_1")
        model.add_regressor("cp_2")
        model.add_regressor("cp_3")
        model.add_regressor("cp_4")
        model.add_regressor("cp_5")
        model.fit(train_df)

        # التنبؤ على فترة الاختبار
        future = test_df[["ds", "temperature", "humidity", "wind_speed",
                          "cp_1", "cp_2", "cp_3", "cp_4", "cp_5"]]
        forecast = model.predict(future)

        # حساب الدقة
        y_true = test_df["y"].values
        y_pred = forecast["yhat"].values
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))

        # حفظ النموذج
        model_path = f"ai_models/prophet/prophet_product_{product_id}.pkl"
        joblib.dump(model, model_path)

        # عرض الدقة
        st.write(f"🔍 دقة النموذج للمنتج {product_id}: MAE = {mae:.2f}, RMSE = {rmse:.2f}")

        # تحديث شريط التقدم
        progress = int(((idx + 1) / total_products) * 100)
        progress_bar.progress(progress)

    st.session_state.retraining_in_progress = False
    return "🎉 تم تدريب كل النماذج بنجاح"