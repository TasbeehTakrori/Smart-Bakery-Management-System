import streamlit as st
from models.customer import Customer
from components import header, footer
from components.layout import apply_rtl
from services import order_service, product_service
from services.product_ai import predict_avg_daily_demand
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="الطلبات", page_icon="🧾", layout="wide")

# ----------------- إعداد الصفحة -----------------
apply_rtl()
header.render()

st.markdown("""
    <h2 style='text-align: center; color: #5D4037; background-color:#FFF8E1;
    padding: 10px; border-radius: 8px;'>🧾 إدارة الطلبات</h2>
""", unsafe_allow_html=True)

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
    forecast_data = []
    for p in products:
        demand = predict_avg_daily_demand(p["id"])
        if demand:
            forecast_data.append({"اسم المنتج": p["name"], "الطلب اليومي المتوقع": demand})

    if forecast_data:
        st.table(pd.DataFrame(forecast_data))
    else:
        st.info("لا توجد بيانات تنبؤ بعد.")

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
