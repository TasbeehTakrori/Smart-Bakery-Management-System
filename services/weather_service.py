import pandas as pd
import requests
from datetime import datetime

# WeatherAPI Key
API_KEY = "87c7874ee8424acab67195650250304"

# --------------------------------
# تحقق من API_KEY
# --------------------------------
if not API_KEY:
    print("🔴 API_KEY غير موجود. تأكد من إضافته.")
else:
    print("✅ API_KEY تم تحميله بنجاح.")

# --------------------------------

def get_historical_weather_data(start_date, end_date, location="Nablus"):
    from datetime import datetime

    # تأكد أن التواريخ عبارة عن datetime وليست نصوص
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    url = "http://api.weatherapi.com/v1/history.json"

    params = {
        "key": API_KEY,
        "q": location,
        "dt": start_date,
        "end_dt": end_date,
        "lang": "en"
    }

    results = []

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "forecast" in data and "forecastday" in data["forecast"]:
                for day in data["forecast"]["forecastday"]:
                    results.append({
                        "ds": day["date"],
                        "temperature": day["day"]["avgtemp_c"],
                        "humidity": day["day"]["avghumidity"],
                        "wind_speed": day["day"]["maxwind_kph"]
                    })
        else:
            print(f"⚠️ فشل في جلب البيانات. الكود: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ خطأ أثناء جلب البيانات: {e}")

    return results
# --------------------------------
# دالة لجلب بيانات الطقس الحالي
# --------------------------------
def get_current_weather(location="Nablus"):
    API_URL = "http://api.weatherapi.com/v1/current.json"

    params = {
        "key": API_KEY,
        "q": location,
        "lang": "en"
    }

    try:
        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            data = response.json()

            if "current" in data:
                temp = data["current"]["temp_c"]
                humidity = data["current"]["humidity"]
                condition = data["current"]["condition"]["text"]
                wind = data["current"]["wind_kph"]
                last_updated = data["current"]["last_updated"]

                print(f"📍 {location} - 📅 {last_updated}")
                print(f"🌡️ درجة الحرارة: {temp}°C")
                print(f"💧 الرطوبة: {humidity}%")
                print(f"💨 سرعة الرياح: {wind} كم/س")
                print(f"☁️ الحالة: {condition}")

                # ✅ إرجاع البيانات
                return {
                    "temperature": temp,
                    "humidity": humidity,
                    "wind_speed": wind,
                    "condition": condition,
                    "last_updated": last_updated
                }

            else:
                print("🔴 لا توجد بيانات حالية.")
                return None

        else:
            print(f"⚠️ فشل في جلب البيانات. كود الاستجابة: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return None



def get_weather_forecast(days=7, location="Nablus"):
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": API_KEY,
        "q": location,
        "days": days,
        "lang": "en"
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            forecast_days = data["forecast"]["forecastday"]
            forecast = []

            for day in forecast_days:
                forecast.append({
                    "ds": pd.to_datetime(day["date"]),
                    "temperature": day["day"]["avgtemp_c"],
                    "humidity": day["day"]["avghumidity"],
                    "wind_speed": day["day"]["maxwind_kph"]
                })

            return forecast
        else:
            print(f"⚠️ فشل في جلب التوقعات. الكود: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ خطأ في الاتصال بالطقس: {e}")
        return None
# --------------------------------
# اختبار الدوال
# --------------------------------
start = datetime(2025, 3, 1)
end = datetime(2025, 3, 20)
location = "32.2226,35.2620"  # إحداثيات نابلس

weather_data = get_historical_weather_data(start, end, location)

# طباعة النتائج بشكل منسق
for row in weather_data:
    print(f"{row['ds']} | 🌡️ {row['temperature']}°C | 💧 {row['humidity']}% | 💨 {row['wind_speed']} kph")

print("\n🌤️ بيانات الطقس الحالي:")
get_current_weather("Nablus")