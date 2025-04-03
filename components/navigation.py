import streamlit as st

def render_main_buttons():
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📦 المنتجات"):
            st.switch_page("pages/products.py")

    with col2:
        if st.button("🛒 الطلبات"):
            st.switch_page("pages/orders.py")

    with col3:
        if st.button("📊 لوحة التحكم"):
            st.switch_page("pages/dashboard.py")
