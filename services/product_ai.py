import os
import joblib
import pandas as pd
from services.weather_service import get_current_weather  # استيراد دالة جلب الطقس
import joblib
import os
from services.weather_service import get_weather_forecast  # تأكدي من وجودها
from services.order_service import get_actual_orders_per_day
from services.weather_service import get_historical_weather_data
from services.checkpoint_service import get_latest_checkpoint_values
from services.checkpoint_service import get_checkpoint_conditions_last_n_days


def predict_avg_daily_demand_with_weather(product_id, days=7, location="Nablus"):
    model_path = f"ai_models/prophet/prophet_product_{product_id}.pkl"

    if not os.path.exists(model_path):
        print(f"❌ لا يوجد نموذج لهذا المنتج: {product_id}")
        return None

    print(f"✅ تحميل النموذج: {model_path}")
    model = joblib.load(model_path)

    print(f"🌤️ جلب توقعات الطقس القادمة لـ {days} يوم...")
    forecast_weather = get_weather_forecast(days=days, location=location)

    if not forecast_weather:
        print("❌ لم يتم جلب بيانات الطقس المستقبلية.")
        return None

    # تحويل إلى DataFrame
    weather_df = pd.DataFrame(forecast_weather)
    latest_checkpoints = get_latest_checkpoint_values()
    checkpoint_df = pd.DataFrame({
        "ds": weather_df["ds"]
    })
    for col, val in latest_checkpoints.items():
        checkpoint_df[col] = val

    weather_df = weather_df.merge(checkpoint_df, on="ds", how="left")
    print(weather_df)

    # توقع الطلب
    try:
        forecast = model.predict(weather_df)
        avg_demand = round(forecast["yhat"].mean(), 1)
        print(f"✅ متوسط الطلب المتوقع خلال {days} يوم: {avg_demand}")
        return avg_demand
    except Exception as e:
        print(f"❌ خطأ أثناء التنبؤ: {e}")
        return None


# دالة التنبؤ بالطلب
from datetime import datetime
import pandas as pd

def predict_daily_demand_with_weather(product_id):
    model_path = f"ai_models/prophet/prophet_product_{product_id}.pkl"

    if not os.path.exists(model_path):
        print(f"❌ النموذج غير موجود للمُنتج {product_id}")
        return None

    print(f"✅ جاري تحميل النموذج من {model_path}")
    model = joblib.load(model_path)

    print("🌦️ محاولة جلب بيانات الطقس الحالية...")
    weather = get_current_weather()

    if weather is None:
        print("❌ لم يتمكن النظام من جلب بيانات الطقس.")
        return None

    print("✅ بيانات الطقس تم جلبها بنجاح:")
    print(weather)

    # 🗓️ تاريخ اليوم (بدون وقت)
    today = pd.to_datetime(datetime.now().date())

    # 📋 تجهيز بيانات الطقس
    weather_data = pd.DataFrame([{
        "ds": today,
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "wind_speed": weather["wind_speed"]
    }])
    print("📋 بيانات الطقس:")
    print(weather_data)

    # ⚙️ توليد future بدون أيام إضافية
    future = model.history[["ds"]].copy()

    # ➕ إضافة اليوم الحالي باستخدام concat بدل append
    new_row = pd.DataFrame([{"ds": today}])
    future = pd.concat([future, new_row], ignore_index=True)
    print(f"future1::::{future}")

    # حذف التكرارات في حال كان تاريخ اليوم موجود مسبقًا
    future = future.drop_duplicates(subset="ds")
    print(f"future2::::{future}")
    # دمج بيانات الطقس
    future = future.merge(weather_data, on="ds", how="left")
    checkpoints = get_latest_checkpoint_values()
    checkpoints_data = pd.DataFrame([{
        "ds": today,
        "cp_1": checkpoints["cp_1"],
        "cp_2": checkpoints["cp_2"],
        "cp_3": checkpoints["cp_3"],
        "cp_4": checkpoints["cp_4"],
        "cp_5": checkpoints["cp_5"]
    }])
    future = future.merge(checkpoints_data, on="ds", how="left")
    print(f"future3::::{future}")

    print("🔄 future بعد الدمج:")
    print(future.tail(3))

    try:
        forecast = model.predict(future)
        today_prediction = forecast[forecast["ds"] == today]["yhat"].values[0]
        print(f"✅ تنبؤ الطلب اليوم {today}: {today_prediction}")
        return today_prediction
    except Exception as e:
        print(f"❌ خطأ أثناء التنبؤ: {e}")
        return None



def get_future_demand_forecast_with_weather(product_id, days=7, location="Nablus"):
    model_path = f"ai_models/prophet/prophet_product_{product_id}.pkl"

    if not os.path.exists(model_path):
        print(f"❌ لا يوجد نموذج للمنتج {product_id}")
        return None

    model = joblib.load(model_path)

    forecast_weather = get_weather_forecast(days=days, location=location)
    if not forecast_weather:
        print("❌ فشل في جلب الطقس المستقبلي.")
        return None
    checkpoints = get_latest_checkpoint_values()
    print("########################")

    weather_df = pd.DataFrame(forecast_weather)

    # نستخدم التواريخ من weather_df
    latest_checkpoints = get_latest_checkpoint_values()
    checkpoint_df = pd.DataFrame({
        "ds": weather_df["ds"]
    })
    for col, val in latest_checkpoints.items():
        checkpoint_df[col] = val

    weather_df = weather_df.merge(checkpoint_df, on="ds", how="left")
    print(f"########################weather_df{weather_df}")

    forecast = model.predict(weather_df)
    return forecast[["ds", "yhat"]]


# --- داخل ملف product_ai.py ---
import pandas as pd
import joblib
import os
from services.weather_service import get_historical_weather_data


def get_prediction_vs_actual_analysis(product_id, days=7):
    model_path = f"ai_models/prophet/prophet_product_{product_id}.pkl"
    if not os.path.exists(model_path):
        return None, None, None, None

    # حساب التواريخ المطلوبة (آخر 7 أيام)
    today = pd.to_datetime("today").normalize()
    date_list = [(today - pd.Timedelta(days=i)) for i in range(days)][::-1]  # تصاعديًا

    # جلب الطقس التاريخي لتلك الفترة
    weather_data = get_historical_weather_data(start_date=date_list[0], end_date=date_list[-1])
    weather_df = pd.DataFrame(weather_data)
    weather_df["ds"] = pd.to_datetime(weather_df["ds"])

    # جلب الطلبات الفعلية من خلال service
    actual_df = get_actual_orders_per_day(product_id, start_date=date_list[0], end_date=date_list[-1])
    print(f"actual_df**: {actual_df}")

    # تجهيز future DataFrame بالتواريخ المطلوبة
    future_df = pd.DataFrame({"ds": date_list})
    future_df = future_df.merge(weather_df, on="ds", how="left")
    print(f"future_df**: {future_df}")

    checkpoints = get_checkpoint_conditions_last_n_days()
    checkpoints_df = pd.DataFrame({"ds":future_df["ds"]})
    checkpoints_df = checkpoints_df.merge(checkpoints, on="ds", how="left")
    print(f"checkpoints_df$$: {checkpoints_df}")

    future_df = future_df.merge(checkpoints_df, on="ds", how="left")
    print(f"future_df: {future_df}")
    # تحميل النموذج والتنبؤ
    model = joblib.load(model_path)
    forecast = model.predict(future_df)

    result_df = future_df[["ds"]].copy()
    result_df["predicted"] = forecast["yhat"]
    result_df = result_df.merge(actual_df, on="ds", how="left")
    result_df["actual"] = result_df["actual"].fillna(0)

    # حساب المقاييس
    result_df["error"] = result_df["actual"] - result_df["predicted"]
    result_df["abs_error"] = result_df["error"].abs()
    result_df["error_percent"] = result_df.apply(
        lambda row: 100 if row["actual"] == 0 and row["predicted"] > 0 else
        0 if row["actual"] == 0 and row["predicted"] == 0 else
        (row["abs_error"] / row["actual"]) * 100,
        axis=1
    )

    mae = result_df["abs_error"].mean()
    mape = result_df["error_percent"].mean()
    accuracy = 100 - mape

    return result_df.sort_values("ds"), mae, mape, accuracy
