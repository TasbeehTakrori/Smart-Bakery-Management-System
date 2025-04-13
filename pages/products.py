import streamlit as st
from components import header, footer
from components.layout import apply_rtl
from services.raw_materials_service import get_raw_materials
from services import product_service
from services.product_ai import  predict_avg_daily_demand_with_weather
from services.order_service import get_latest_order_date
from ml.train_prophet_models import retrain_prophet_models_with_weather
from datetime import datetime, timedelta
import os
import io
import base64
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# ----------------- إعداد الصفحة -----------------
st.set_page_config(page_title="المنتجات", page_icon="📦", layout="wide")
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

# ----------------- الخط العربي -----------------
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Cairo', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- العنوان -----------------
st.markdown("""
    <h2 style='text-align: center; color: #5D4037; background-color:#FFF8E1;
    padding: 10px; border-radius: 8px;'>📦 إحصائيات المنتجات</h2>
""", unsafe_allow_html=True)
st.markdown(' ')
# ----------------- أدوات مساعدة -----------------
def display_local_image(path: str, width: int = 280):
    if not os.path.exists(path):
        path = "images/default.png"
    with open(path, "rb") as img_file:
        img_bytes = img_file.read()
        encoded = base64.b64encode(img_bytes).decode()
        img_html = f"<img src='data:image/jpeg;base64,{encoded}' width='{width}' style='border-radius:10px;'>"
        st.markdown(img_html, unsafe_allow_html=True)

# ----------------- عرض المنتج -----------------
def render_product_card(product, demand):
    st.markdown("<div style='background-color:#FFFDF6; padding:15px; border-radius:12px; margin-bottom:20px; box-shadow:0 2px 8px #ccc;'>", unsafe_allow_html=True)
    cols = st.columns([1, 3])

    with cols[0]:
        display_local_image(product.get("image_url"), width=240)
        st.markdown('')
        in_col1, in_col2, in_col3 = st.columns([1, 1, 1])
        with in_col1:
            if st.button("✏️ تعديل", key=f"toggle_edit_{product['id']}"):
                st.session_state[f"edit_{product['id']}"] = not st.session_state.get(f"edit_{product['id']}", False)
        with in_col2:
            if st.button("🗑️ حذف", key=f"delete_{product['id']}"):
                product_service.delete_product(product['id'])
                st.success("✅ تم حذف المنتج.")
                st.rerun()
        with in_col3:
            if st.button("المواد الخام", key=f"toggle_add_edit_raw_material_{product['id']}"):
                st.session_state[f"add_edit_raw_material_{product['id']}"] = not st.session_state.get(f"add_edit_raw_material_{product['id']}", False)


    with cols[1]:
        st.markdown(f"<h4 style='color:#4E342E;'>{product['name']}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>💰 السعر:</strong> <span style='color:green;'>{product['price']} ₪</span></p>", unsafe_allow_html=True)

        stock = product["stock"]
        stock_display = f"<span style='color:red;'>⚠️ {stock} فقط!</span>" if stock < 5 else f"{stock}"
        st.markdown(f"<p><strong>📦 الكمية:</strong> {stock_display}</p>", unsafe_allow_html=True)

        if demand is not None:
            days_to_empty = stock / demand
            if days_to_empty < 7:
                st.markdown(f"<p style='color:red;'>🔮 متوقع النفاد خلال <strong>{days_to_empty:.1f} يوم</strong></p>", unsafe_allow_html=True)

        st.markdown(f"<p><strong>📝 الوصف:</strong> {product['description']}</p>", unsafe_allow_html=True)
        # 📅 عرض تاريخ الإضافة
        if product.get("created_at"):
            formatted_date = product["created_at"].strftime("%Y-%m-%d %H:%M")
            st.markdown(f"<p><strong>📅 أضيف في:</strong> {formatted_date}</p>", unsafe_allow_html=True)

        # 🕒 عرض تاريخ آخر طلب
        latest_order = get_latest_order_date(product["id"])
        if latest_order:
            st.markdown(f"<p><strong>🕒 آخر طلب:</strong> {latest_order.strftime('%Y/%m/%d')}</p>",
                        unsafe_allow_html=True)

    if st.session_state.get(f"edit_{product['id']}", False):
        render_edit_form(product)
    if st.session_state.get(f"add_edit_raw_material_{product['id']}", False):
        raw_material_edit_form(product)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- تعديل المنتج -----------------
def render_edit_form(product):
    with st.expander("📝 تعديل المنتج", expanded=True):
        with st.form(f"edit_form_{product['id']}"):
            name = st.text_input("اسم المنتج", value=product["name"])
            description = st.text_area("الوصف", value=product["description"])
            price = st.number_input("السعر بالشيكل (₪)", min_value=0.5, step=0.5, format="%.1f", value=product["price"])
            stock = st.number_input("الكمية المتوفرة", min_value=0, value=product["stock"])

            uploaded_file = st.file_uploader("📸 صورة جديدة (اختياري)", type=["png", "jpg", "jpeg"], key=f"edit_img_{product['id']}")
            image_filename = product.get("image_url")

            if uploaded_file:
                image_filename = f"images/{uploaded_file.name}"
                with open(image_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            if st.form_submit_button("📏 حفظ التعديلات"):
                updated_product = {
                    "name": name,
                    "description": description,
                    "price": price,
                    "stock": stock,
                    "image_url": image_filename
                }
                product_service.update_product(product["id"], updated_product)
                st.success("✅ تم تعديل المنتج بنجاح.")
                st.rerun()

def raw_material_edit_form(product):
    with st.expander("📝 تعديل المواد الخام", expanded=True):

            st.markdown("### المواد الخام")
            raw_materials =  get_raw_materials()
            raw_material_names = [material.name for material in raw_materials]

            selected_materials = st.multiselect("اختر المواد الخام", raw_material_names)

            raw_material_quantities = {}

            # Dynamically generate number_input for each selected material inside the form
            for material in selected_materials:
                quantity = st.number_input(f"كمية ال{material} لكيلو واحد من {product['name']} ", min_value=0.00, step=0.05, key=f"quantity_{material}_{product['id']}")
                if quantity > 0:
                    raw_material_quantities[material] = quantity

            if st.button("إضافة المواد الخام"):
                product_service.remove_all_raw_materials_for_product(product['id'])
                # إضافة المواد الخام والكميات إلى قاعدة البيانات
                for material, quantity in raw_material_quantities.items():
                    product_service.add_product_ingredient(product['id'], material, quantity)
                st.success("✅ تم إضافة المواد الخام بنجاح.")





# ----------------- عرض المنتجات -----------------
products = product_service.get_products()

if products:

    total_products = len(products)
    average_price = sum(p["price"] for p in products) / total_products
    total_stock = sum(p["stock"] for p in products)

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 عدد المنتجات", total_products)
    col2.metric("💰 متوسط السعر", f"{average_price:.2f} ₪")
    col3.metric("📊 إجمالي الكمية", total_stock)

    st.markdown(' ')
    # ----------------- رسم بياني تفاعلي -----------------
    st.markdown("""
    <h3 style='text-align: center; color: #5D4037; background-color:#FFF8E1;
    padding: 10px; border-radius: 8px;'>📊 رسم بياني: اسم المنتج مقابل الكمية</h3>
""", unsafe_allow_html=True)

    chart_df = pd.DataFrame(products)
    fig = px.bar(
        chart_df,
        x="name",
        y="stock",
        labels={"name": "اسم المنتج", "stock": "الكمية"},
        title="كمية المنتجات الحالية",
        text="stock",
        color_discrete_sequence=["#6D4C41"]
    )
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode="hide", font=dict(family="Cairo, sans-serif", size=14))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🧁 قائمة المنتجات", unsafe_allow_html=True)

    # ----------------- عرض كل بطاقة منتج -----------------
    for product in products:
        demand = predict_avg_daily_demand_with_weather(product["id"])
        print(f"Demand={demand}")
        render_product_card(product, demand)
else:
    st.info("لا توجد منتجات بعد.")

# ----------------- حذف الكل -----------------
if st.button("🗑️ حذف كل المنتجات"):
    product_service.delete_all_products()
    st.success("✅ تم حذف كل المنتجات.")
    st.rerun()

# ----------------- إضافة منتج جديد -----------------

import streamlit as st
from datetime import datetime

# إعداد الصفحة
st.markdown("### ➕ إضافة منتج جديد")

# نموذج لإضافة المنتج
with st.form("add_product_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("اسم المنتج")
        description = st.text_area("وصف المنتج")
        uploaded_file = st.file_uploader("📸 صورة المنتج", type=["png", "jpg", "jpeg"])
        image_filename = None
        if uploaded_file:
            image_filename = f"images/{uploaded_file.name}"
            with open(image_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())

    with col2:
        price = st.number_input("السعر بالشيكل (₪)", min_value=0.5, step=0.5, format="%.1f")
        stock = st.number_input("الكمية المتوفرة", min_value=0)

    # زر لإرسال نموذج المنتج
    product_submit_button = st.form_submit_button("إضافة المنتج")

if product_submit_button:
    # إضافة المنتج إلى قاعدة البيانات
    new_product = {
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "image_url": image_filename or "images/default.png",
        "created_at": datetime.now()
    }

    # إضافة المنتج
    product_service.add_product(new_product)
    st.success("✅ تم إضافة المنتج بنجاح.")
    st.rerun()
#-------- إعادة تدريب النماذج ----------

# عند الضغط على الزر
if st.button("🔄 إعادة تدريب نماذج Prophet لجميع المنتجات"):
    result = retrain_prophet_models_with_weather()
    st.success(result)
# ----------------- تصدير CSV -----------------
st.markdown("---")
st.markdown("### 📟 تصدير المنتجات")

if products:
    df = pd.DataFrame(products)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    st.download_button(
        label="📅 تحميل كملف CSV",
        data=csv_buffer.getvalue().encode("utf-8-sig"),
        file_name="products.csv",
        mime="text/csv"
    )
else:
    st.info("لا توجد بيانات للتصدير.")

# ----------------- التذييل -----------------
footer.render()