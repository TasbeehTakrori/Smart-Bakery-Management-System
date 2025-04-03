import streamlit as st

def apply_rtl():
    st.markdown("""
        <style>
            html, body, [class*="css"] {
                direction: rtl;
                text-align: right;
            }
        </style>
    """, unsafe_allow_html=True)
