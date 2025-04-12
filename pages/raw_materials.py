import streamlit as st
from components import header, footer
from components.layout import apply_rtl
from services import raw_materials_service
from datetime import datetime
import pandas as pd
import plotly.express as px

import streamlit as st
from services import product_service
import pandas as pd
import plotly.express as px

import os
import io
import base64

# إعداد الصفحة
st.set_page_config(page_title="إدارة المواد الخام", page_icon="📦", layout="wide")
apply_rtl()
header.render()

# العنوان
st.markdown("""
    <h2 style='text-align: center; color: #5D4037; background-color:#FFF8E1;
    padding: 10px; border-radius: 8px;'>📦 إدارة المواد الخام</h2>
""", unsafe_allow_html=True)



raw_materials = raw_materials_service.get_raw_materials()

if raw_materials:
    # استرجاع الطلب المتوقع لكل مادة خام
    raw_material_demand = raw_materials_service.get_raw_material_demand()
    print(raw_material_demand)
    # إنشاء إطار بيانات لعرض المواد الخام مع الطلب المتوقع
    raw_material_data = []
    for material in raw_materials:
        material_name = material.name
        quantity_in_stock = material.quantity_in_stock
        expected_demand = raw_material_demand.get(material_name, 0)
        raw_material_data.append({
            "اسم المادة الخام": material_name,
            "الكمية المتوفرة": quantity_in_stock,
            "الطلب المتوقع": expected_demand,
        })

    # عرض البيانات في جدول
    df = pd.DataFrame(raw_material_data)
    st.dataframe(df)

else:
    st.info("لا توجد مواد خام بعد.")


# ----------------- عرض المادة الخام -----------------
def render_raw_material_card(raw_material):
    st.markdown("<div style='background-color:#FFFDF6; padding:15px; border-radius:12px; margin-bottom:20px; box-shadow:0 2px 8px #ccc;'>", unsafe_allow_html=True)
    cols = st.columns([1, 3])

    with cols[0]:
        # display_local_image(raw_material.get("image_url"), width=240)
        st.markdown('')
        in_col1, in_col2 = st.columns([1, 1])
        with in_col1:
            if st.button("✏️ تعديل", key=f"toggle_edit_{raw_material.id}"):
                st.session_state[f"edit_{raw_material.id}"] = not st.session_state.get(f"edit_{raw_material.id}", False)
        with in_col2:
            if st.button("🗑️ حذف", key=f"delete_{raw_material.id}"):
                raw_materials_service.delete_raw_material(raw_material.id)
                st.success("✅ تم حذف المادة الخام.")
                st.rerun()

    with cols[1]:
        st.markdown(f"<h4 style='color:#4E342E;'>{raw_material.name}</h4>", unsafe_allow_html=True)

        stock = raw_material.quantity_in_stock
        stock_display = f"<span style='color:red;'>⚠️ {stock} فقط!</span>" if stock < 5 else f"{stock}"
        st.markdown(f"<p><strong>📦 الكمية المتوفرة:</strong> {stock_display}</p>", unsafe_allow_html=True)


    if st.session_state.get(f"edit_{raw_material.id}", False):
        render_edit_form(raw_material)

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- تعديل المادة الخام -----------------
def render_edit_form(raw_material):
    with st.expander("📝 تعديل المادة الخام", expanded=True):
        with st.form(f"edit_form_{raw_material.id}"):
            name = st.text_input("اسم المادة الخام", value=raw_material.name)
            quantity_in_stock = st.number_input("الكمية المتوفرة", min_value=0, value=raw_material.quantity_in_stock)

            if st.form_submit_button("📏 حفظ التعديلات"):
                updated_raw_material = {
                    "name": name,
                    "price_per_unit": 0,
                    "quantity_in_stock": quantity_in_stock
                }
                raw_materials_service.update_raw_material(raw_material.id, updated_raw_material)
                st.success("✅ تم تعديل المادة الخام بنجاح.")
                st.rerun()

# ----------------- عرض المواد الخام -----------------
raw_materials = raw_materials_service.get_raw_materials()

if raw_materials:
    total_raw_materials = len(raw_materials)
    total_quantity = sum(r.quantity_in_stock for r in raw_materials)  # تعديل الوصول إلى السمات مباشرة

    col1, col2 = st.columns(2)
    col1.metric("📦 عدد المواد الخام", total_raw_materials)
    col2.metric("📊 إجمالي الكمية المتوفرة", total_quantity)

    st.markdown(' ')

    st.markdown("""
    <h3 style='text-align: center; color: #5D4037; background-color:#FFF8E1;
    padding: 10px; border-radius: 8px;'>📊 رسم بياني: اسم المادة الخام مقابل الكمية المتوفرة</h3>
    """, unsafe_allow_html=True)

    # تحويل المواد الخام إلى DataFrame
    chart_df = pd.DataFrame([{
        "name": r.name,
        "quantity_in_stock": r.quantity_in_stock
    } for r in raw_materials])

    fig = px.bar(
        chart_df,
        x="name",
        y="quantity_in_stock",
        labels={"name": "اسم المادة الخام", "quantity_in_stock": "الكمية المتوفرة"},
        title="كمية المواد الخام المتوفرة",
        text="quantity_in_stock",
        color_discrete_sequence=["#6D4C41"]
    )
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode="hide", font=dict(family="Cairo, sans-serif", size=14))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🧑‍🍳 قائمة المواد الخام", unsafe_allow_html=True)

    # ----------------- عرض كل بطاقة مادة خام -----------------
    for raw_material in raw_materials:
        render_raw_material_card(raw_material)
else:
    st.info("لا توجد مواد خام بعد.")

# ----------------- إضافة مادة خام جديدة -----------------
st.markdown("---")
st.markdown("### ➕ إضافة مادة خام جديدة", unsafe_allow_html=True)

# في نموذج إضافة المادة الخام:
with st.form("add_raw_material_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("اسم المادة الخام")
    with col2:
        quantity_in_stock = st.number_input("الكمية المتوفرة", min_value=0)

    if st.form_submit_button("إضافة المادة الخام"):
        new_raw_material = {
            "name": name,
            "price_per_unit": 0,
            "quantity_in_stock": quantity_in_stock,
            "created_at": datetime.now()
        }
        raw_materials_service.add_raw_material(new_raw_material)
        st.success("✅ تم إضافة المادة الخام بنجاح.")
        st.rerun()

# ----------------- تصدير CSV -----------------
st.markdown("---")
st.markdown("### 📟 تصدير المواد الخام")

if raw_materials:
    df = pd.DataFrame(raw_materials)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    st.download_button(
        label="📅 تحميل كملف CSV",
        data=csv_buffer.getvalue().encode("utf-8-sig"),
        file_name="raw_materials.csv",
        mime="text/csv"
    )
else:
    st.info("لا توجد بيانات للتصدير.")

# ----------------- التذييل -----------------
footer.render()