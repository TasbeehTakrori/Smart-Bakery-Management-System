import streamlit as st
from components import header, footer
from services import product_service
from components.layout import apply_rtl
import os
import pandas as pd
import io

# إعداد الصفحة
st.set_page_config(
    page_title="المنتجات",
    page_icon="📦",
    layout="wide"
)

apply_rtl()
header.render()

# ---------- تنسيق الخط العربي ----------
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Cairo', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- عنوان رئيسي ----------
st.markdown("<h2 style='text-align: right; color: #5D4037; background-color:#FFF8E1; padding: 10px; border-radius: 8px;'>📦 إدارة المنتجات</h2>", unsafe_allow_html=True)

# ---------- دالة عرض منتج ----------
def render_product_card(product):
    st.markdown("<div style='background-color:#FFF3E0; padding:15px; border-radius:10px; margin-bottom:20px; box-shadow:0 0 8px #ccc;'>", unsafe_allow_html=True)

    cols = st.columns([1, 3])
    with cols[0]:
        image_path = product.get("image_url") or "images/default.png"
        if not os.path.exists(image_path):
            image_path = "images/default.png"
        st.image(image_path, width=130)

    with cols[1]:
        st.markdown(f"<h4 style='color:#6D4C41;'>{product['name']}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>💰 السعر:</strong> {product['price']} ₪</p>", unsafe_allow_html=True)
        # تنبيه إذا الكمية أقل من 5
        if product["stock"] < 5:
            stock_display = f"<span style='color:red;'>⚠️ {product['stock']} فقط!</span>"
        else:
            stock_display = f"{product['stock']}"

        st.markdown(f"<p><strong>📦 الكمية:</strong> {stock_display}</p>", unsafe_allow_html=True)

        st.markdown(f"<p><strong>📝 الوصف:</strong> {product['description']}</p>", unsafe_allow_html=True)

        if st.button("🗑️ حذف المنتج", key=f"delete_{product['id']}"):
            product_service.delete_product(product['id'])
            st.success("✅ تم حذف المنتج.")
            st.rerun()

        if st.button("✏️ تعديل", key=f"toggle_edit_{product['id']}"):
            st.session_state[f"edit_{product['id']}"] = not st.session_state.get(f"edit_{product['id']}", False)

    if st.session_state.get(f"edit_{product['id']}", False):
        render_edit_form(product)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- دالة تعديل منتج ----------
def render_edit_form(product):
    with st.expander("📝 تعديل المنتج", expanded=True):
        with st.form(f"edit_form_{product['id']}"):
            name = st.text_input("اسم المنتج", value=product["name"])
            description = st.text_area("الوصف", value=product["description"])
            price = st.number_input("السعر بالشيكل (₪)", min_value=0.5, step=0.5, format="%.1f", value=product["price"])
            stock = st.number_input("الكمية المتوفرة", min_value=0, value=product["stock"])

            uploaded_file = st.file_uploader("📸 صورة جديدة (اختياري)", type=["png", "jpg", "jpeg"], key=f"edit_img_{product['id']}")
            image_filename = product.get("image_url")

            if uploaded_file is not None:
                image_filename = f"images/{uploaded_file.name}"
                with open(image_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            submitted = st.form_submit_button("💾 حفظ التعديلات")
            if submitted:
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

# ---------- عرض المنتجات ----------
products = product_service.get_products()

# ---------- إحصائيات بسيطة ----------
if products:
    total_products = len(products)
    average_price = sum([p["price"] for p in products]) / total_products
    total_stock = sum([p["stock"] for p in products])

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 عدد المنتجات", total_products)
    col2.metric("💰 متوسط السعر", f"{average_price:.2f} ₪")
    col3.metric("📊 إجمالي الكمية", total_stock)


if products:
    for product in products:
        render_product_card(product)
else:
    st.info("لا توجد منتجات بعد.")


# ---------- زر حذف الكل ----------
if st.button("🗑️ حذف كل المنتجات"):
    product_service.delete_all_products()
    st.success("✅ تم حذف كل المنتجات.")
    st.rerun()

# ---------- إضافة منتج جديد ----------
st.markdown("---")
st.markdown("### ➕ إضافة منتج جديد", unsafe_allow_html=True)

with st.form("add_product_form"):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("اسم المنتج")
        description = st.text_area("وصف المنتج")
        uploaded_file = st.file_uploader("📸 صورة المنتج", type=["png", "jpg", "jpeg"])
        image_filename = None
        if uploaded_file is not None:
            image_filename = f"images/{uploaded_file.name}"
            with open(image_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())

    with col2:
        price = st.number_input("السعر بالشيكل (₪)", min_value=0.5, step=0.5, format="%.1f")
        stock = st.number_input("الكمية المتوفرة", min_value=0)

    submitted = st.form_submit_button("إضافة المنتج")
    if submitted:
        new_product = {
            "name": name,
            "description": description,
            "price": price,
            "stock": stock,
            "image_url": image_filename or "images/default.png"
        }
        product_service.add_product(new_product)
        st.success("✅ تم إضافة المنتج بنجاح.")
        st.rerun()

# --- تصدير البيانات إلى CSV ---
st.markdown("---")
st.markdown("### 🧾 تصدير المنتجات")

if products:
    df = pd.DataFrame(products)

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    csv_bytes = csv_buffer.getvalue().encode("utf-8-sig")

    st.download_button(
        label="📥 تحميل المنتجات كملف CSV",
        data=csv_bytes,
        file_name="products.csv",
        mime="text/csv"
    )
else:
    st.info("لا توجد بيانات للتصدير.")


footer.render()
