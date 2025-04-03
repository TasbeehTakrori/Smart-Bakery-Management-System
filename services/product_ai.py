import os
import joblib
import pandas as pd
from services.weather_service import get_current_weather  # استيراد دالة جلب الطقس
import joblib
import os
from services.weather_service import get_weather_forecast  # تأكدي من وجودها

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
    print("📋 بيانات الطقس المستقبلية:")
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
    future = model.history[["ds"]].copy()  # فقط التواريخ السابقة

    # ➕ إضافة اليوم الحالي باستخدام concat بدل append
    new_row = pd.DataFrame([{"ds": today}])
    future = pd.concat([future, new_row], ignore_index=True)

    # حذف التكرارات في حال كان تاريخ اليوم موجود مسبقًا
    future = future.drop_duplicates(subset="ds")

    # دمج بيانات الطقس
    future = future.merge(weather_data, on="ds", how="left")

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