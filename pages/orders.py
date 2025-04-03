import streamlit as st
from components import header, footer
from components.layout import apply_rtl
from services import order_service, product_service
from services.product_ai import get_daily_demand_forecast
from services.order_service import get_latest_order_date
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="الطلبات", page_icon="🧾", layout="wide")

# ----------------- إعداد الصفحة -----------------
apply_rtl()
header.render()

# خريطة ترجمة أيام الأسبوع إلى العربية
arabic_days = {
    "Saturday": "السبت",
    "Sunday": "الأحد",
    "Monday": "الاثنين",
    "Tuesday": "الثلاثاء",
    "Wednesday": "الأربعاء",
    "Thursday": "الخميس",
    "Friday": "الجمعة",
}

st.markdown("""
    <h2 style='text-align: center; color: #5D4037; background-color:#FFF8E1;
    padding: 10px; border-radius: 8px;'>🧾 إدارة الطلبات</h2>
""", unsafe_allow_html=True)


def render_product_card(product):
    st.markdown("<div style='background-color:#FFFDF6; padding:15px; border-radius:12px; margin-bottom:20px; box-shadow:0 2px 8px #ccc;'>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:#4E342E;'>{product['name']}</h4>", unsafe_allow_html=True)
    stock = product["stock"]
    stock_display = f"<span style='color:red;'>⚠️ {stock} فقط!</span>" if stock < 5 else f"{stock}"
    st.markdown(f"<p><strong>📦 الكمية:</strong> {stock_display}</p>", unsafe_allow_html=True)

    # 🕒 عرض تاريخ آخر طلب
    latest_order = get_latest_order_date(product["id"])
    if latest_order:
        st.markdown(f"<p><strong>🕒 آخر طلب:</strong> {latest_order.strftime('%Y/%m/%d')}</p>",
                    unsafe_allow_html=True)

    # رسم توقع الطلب اليومي
    forecast_df = get_daily_demand_forecast(product["id"])
    if forecast_df is not None:
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        forecast_df = forecast_df[forecast_df["ds"].between(yesterday, today + timedelta(days=6))].copy()
        forecast_df["day"] = forecast_df["ds"].apply(
            lambda d: f"{arabic_days[d.strftime('%A')]} - {d.strftime('%Y/%m/%d')}")
        today_str = f"{arabic_days[today.strftime('%A')]} - {today.strftime('%Y/%m/%d')}"
        forecast_df["color"] = forecast_df["day"].apply(lambda d: "red" if d == today_str else "#6D4C41")

        st.markdown("<p><strong>📈 توقع الطلب القادم:</strong></p>", unsafe_allow_html=True)
        fig = px.line(
            forecast_df,
            x="day",
            y="yhat",
            labels={"day": "اليوم والتاريخ", "yhat": "الطلب المتوقع"},
            title="توقع الطلب اليومي",
            markers=True
        )
        fig.update_traces(marker=dict(size=6))
        fig.update_traces(marker_color=forecast_df["color"], line_color="#6D4C41")
        fig.update_layout(
            font=dict(family="Cairo, sans-serif", size=12),
            xaxis_title="اليوم",
            yaxis_title="الطلب المتوقع",
            margin=dict(t=30, b=20),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

        # إضافة التنبؤ اليومي مع الكمية المتوقعة للإنتاج
        today_demand = forecast_df[forecast_df["day"].str.contains(today_str)]["yhat"].values
        if today_demand:
            st.markdown(f"<p><strong>الطلب المتوقع اليوم للمنتج:</strong> {today_demand[0]:.1f} وحدة</p>", unsafe_allow_html=True)

            # هنا يمكن أن نضيف الكمية المطلوبة للإنتاج بناءً على التنبؤ:
            production_needed = today_demand[0] - product["stock"]
            if production_needed > 0:
                st.markdown(f"<p style='color:red;'><strong>تحتاج إلى إنتاج:</strong> {production_needed:.1f} وحدة اليوم لتغطية الطلب.</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color:green;'><strong>الكمية كافية:</strong> الإنتاج يكفي لتغطية الطلب.</p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ----------------- التبويبات -----------------
tab1, tab2, tab3, tab4 = st.tabs(["🕒 الطلبات", "👥 الزبائن", "🔮 التوقعات", "📊 الأداء العام"])

# ----------------- تبويب الطلبات -----------------
with tab1:
    st.markdown("### 📊 الطلبات اليومية حسب المنتج (آخر ٧ أيام)", unsafe_allow_html=True)

    recent_orders = order_service.get_recent_orders(days=7)  # تأكد من دعم days
    if recent_orders:
        df = pd.DataFrame(recent_orders)
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['day'] = df['order_date'].dt.strftime("%Y-%m-%d")

        daily_summary = df.groupby(['day', 'product_name'])['quantity'].sum().reset_index()

        fig = px.bar(
            daily_summary,
            x="day",
            y="quantity",
            color="product_name",
            labels={"day": "اليوم", "quantity": "الكمية المطلوبة", "product_name": "المنتج"},
            title="📊 الطلبات اليومية حسب المنتج",
            barmode="group",
            height=400,
            text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            font=dict(family="Cairo, sans-serif", size=14),
            xaxis_title="اليوم",
            yaxis_title="الكمية",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات للسبعة أيام الماضية.")

# ----------------- تبويب الزبائن -----------------
with tab2:
    st.markdown("### 👥 الزبائن المتكررين", unsafe_allow_html=True)
    repeat_customers = order_service.get_repeat_customers()
    if repeat_customers:
        st.table(pd.DataFrame(repeat_customers))
    else:
        st.info("لا توجد بيانات زبائن متكررين.")

# ----------------- تبويب التوقعات -----------------
with tab3:
    st.markdown("### 🔮 توقع الطلبات القادمة", unsafe_allow_html=True)
    products = product_service.get_products()
    for p in products:
        render_product_card(p)

# ----------------- تبويب الأداء العام -----------------
with tab4:
    st.markdown("### 📦 إجمالي الكمية المطلوبة حسب المنتج", unsafe_allow_html=True)
    total_quantities = order_service.get_total_quantity_by_product()
    if total_quantities:
        df = pd.DataFrame(total_quantities)
        product_names = {p['id']: p['name'] for p in product_service.get_products()}
        df["name"] = df["product_id"].map(product_names)
        fig = px.bar(df, x="name", y="total_quantity", text="total_quantity",
                     labels={"name": "اسم المنتج", "total_quantity": "إجمالي الكمية المطلوبة"},
                     title="📦 إجمالي الكمية المُباعة لكل منتج",
                     color_discrete_sequence=["#6D4C41"])
        fig.update_layout(font=dict(family="Cairo, sans-serif"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات لعرضها.")

footer.render()