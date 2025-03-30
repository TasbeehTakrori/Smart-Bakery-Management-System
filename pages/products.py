import streamlit as st
from components import header, footer
from services import product_service
from components.layout import apply_rtl
import os

# إعداد الصفحة
st.set_page_config(
    page_title="المنتجات",
    page_icon="📦",
    layout="wide"
)

apply_rtl()
header.render()

# ألوان وخط افتراضي
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Cairo', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: right; color: #5D4037; background-color:#FFF8E1; padding: 10px; border-radius: 8px;'>📦 إدارة المنتجات</h2>", unsafe_allow_html=True)

# زر حذف الكل
if st.button("🗑️ حذف كل المنتجات"):
    product_service.delete_all_products()
    st.success("✅ تم حذف كل المنتجات.")
    st.rerun()

# قائمة المنتجات
st.markdown("### 🧁 قائمة المنتجات", unsafe_allow_html=True)
products = product_service.get_products()

if products:
    for product in products:
        st.markdown("""
            <div style='background-color:#FFF3E0; padding:15px; border-radius:10px; margin-bottom:20px; box-shadow:0 0 8px #ccc;'>
        """, unsafe_allow_html=True)

        cols = st.columns([1, 3])
        with cols[0]:
            image_path = product.get("image_url") or "images/default.png"
            if not os.path.exists(image_path):  # تحقق أن الصورة موجودة فعلًا
                image_path = "images/default.png"
            st.image(image_path, width=130)

        with cols[1]:
            st.markdown(f"<h4 style='color:#6D4C41;'>{product['name']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p><strong>💰 السعر:</strong> {product['price']} ₪</p>", unsafe_allow_html=True)
            st.markdown(f"<p><strong>📦 الكمية:</strong> {product['stock']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p><strong>📝 الوصف:</strong> {product['description']}</p>", unsafe_allow_html=True)

            # زر حذف فردي
            if st.button("🗑️ حذف هذا المنتج", key=f"delete_{product['id']}"):
                product_service.delete_product(product['id'])
                st.success("✅ تم حذف المنتج.")
                st.rerun()

        with st.expander("✏️ تعديل المنتج"):
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

        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("لا توجد منتجات بعد.")

# --- إضافة منتج جديد ---
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

footer.render()
