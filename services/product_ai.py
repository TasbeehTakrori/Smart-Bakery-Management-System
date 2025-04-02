import os

import joblib


# --- دالة: توقع متوسط الطلب اليومي للأيام القادمة باستخدام النموذج المحفوظ ---
def predict_avg_daily_demand(product_id, days: int = 7):
    model_path = f"ai_models/prophet/prophet_product_{product_id}.pkl"

    if not os.path.exists(model_path):
        return None  # لا يوجد نموذج محفوظ لهذا المنتج

    model = joblib.load(model_path)
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    avg_demand = forecast.tail(days)["yhat"].mean()
    return round(avg_demand, 1)



def get_daily_demand_forecast(product_id, days: int = 14):
    model_path = f"ai_models/prophet/prophet_product_{product_id}.pkl"

    if not os.path.exists(model_path):
        return None

    model = joblib.load(model_path)
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    return forecast[["ds", "yhat"]].tail(days)


