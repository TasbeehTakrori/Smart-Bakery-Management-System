import streamlit as st
from components import header, footer, navigation
from components.layout import apply_rtl
from models.init_db import init_db
init_db()

# إعداد الصفحة
st.set_page_config(
    page_title="نظام إدارة المخبز الذكي",
    page_icon="🍞",
    layout="wide"
)
apply_rtl()


# --- Header ---
header.render()

# --- Hero Section ---
st.markdown("""
<div style='text-align: center; direction: rtl; padding: 2rem; background-color: #FFF7E6; border-radius: 20px; margin-bottom: 30px;'>
    <h2 style='color: #6B3E26;'>مرحبًا بك في نظام إدارة المخبز الذكي 🍰</h2>
    <p style='font-size: 18px;'>
        نظام شامل يساعدك في تتبع المنتجات، الطلبات، والمخزون، مع دعم للذكاء الاصطناعي لتحسين الأداء.
    </p>
</div>
""", unsafe_allow_html=True)

# --- Navigation Cards ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='text-align: center; direction: rtl; background-color: #F9F3EC; padding: 20px; border-radius: 15px; box-shadow: 0px 0px 8px #eee;'>
        <h4>📦 المنتجات</h4>
        <p>إدارة جميع منتجات المخبز</p>
        """, unsafe_allow_html=True)
    if st.button("الذهاب إلى المنتجات", key="btn_products"):
        st.switch_page("pages/products.py")

with col2:
    st.markdown("""
    <div style='text-align: center; direction: rtl; background-color: #F9F3EC; padding: 20px; border-radius: 15px; box-shadow: 0px 0px 8px #eee;'>
        <h4>🛒 إدارةالطلبات</h4>
        <p>توقع الطلبات اليومية والإنتاج المطلوب لتغطيتها</p>
        """, unsafe_allow_html=True)
    if st.button("الذهاب إلى الطلبات", key="btn_orders"):
        st.switch_page("pages/orders.py")

with col3:
    st.markdown("""
    <div style='text-align: center; direction: rtl; background-color: #F9F3EC; padding: 20px; border-radius: 15px; box-shadow: 0px 0px 8px #eee;'>
        <h4>📊 لوحة التحكم</h4>
        <p>تحليلات الأداء والمبيعات والمخزون</p>
        """, unsafe_allow_html=True)
    if st.button("الذهاب إلى لوحة التحكم", key="btn_dashboard"):
        st.switch_page("./pages/dashboard.py")

# --- Footer ---
footer.render()
