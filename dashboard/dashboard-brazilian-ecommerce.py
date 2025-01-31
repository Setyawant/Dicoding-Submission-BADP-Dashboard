import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud, STOPWORDS

# Konfigurasi awal Streamlit
st.set_page_config(page_title="Brazilian E-commerce Dashboard", page_icon="📊", layout="wide")

#################### Data Processing Code ####################
# Load Data 
@st.cache_data
def load_data():
    df = pd.read_csv("./dashboard/all_rfm_cust_data.csv")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["year_month"] = pd.to_datetime(df["year_month"])
    df["order_approved_at"] = pd.to_datetime(df["order_approved_at"])
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
    df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"])
    df["order_delivered_carrier_date"] = pd.to_datetime(df["order_delivered_carrier_date"])
    
    return df

# Inisialisasi session_state untuk data jika belum ada
if "cust_df" not in st.session_state:
    st.session_state.cust_df = load_data()

# Gunakan data dari session state, tanpa memuat ulang
cust_df = st.session_state.cust_df  

# Ambil min & max tanggal dari dataset
min_date = cust_df['order_purchase_timestamp'].min()
max_date = cust_df['order_purchase_timestamp'].max()

# Inisialisasi session_state untuk filter jika belum ada
if "selected_date_range" not in st.session_state:
    st.session_state.selected_date_range = (min_date, max_date)

if "selected_city" not in st.session_state:
    st.session_state.selected_city = "All"

if "selected_state" not in st.session_state:
    st.session_state.selected_state = "All"


#################### Streamlit UI Code ####################

# Page Setup
home_1_page = st.Page(page="app_pages/dashboard-home.py", title="Home", icon="🏠", default=True)
order_2_page = st.Page(page="app_pages/dashboard-order.py", title="Orders Overview", icon="📦")
customer_3_page = st.Page(page="app_pages/dashboard-customer.py", title="Customers Analysis", icon="🛒")
seller_4_page = st.Page(page="app_pages/dashboard-seller.py", title="Sellers Performance", icon="🏬")
product_5_page = st.Page(page="app_pages/dashboard-product.py", title="Product Analysis", icon="🛍️")
payment_6_page = st.Page(page="app_pages/dashboard-payment.py", title="Payments & Revenue", icon="💳")
review_7_page = st.Page(page="app_pages/dashboard-review.py", title="Reviews & Ratings", icon="⭐")

# Navigation setup
pg = st.navigation(
    pages= [home_1_page, order_2_page, customer_3_page, seller_4_page, product_5_page, payment_6_page, review_7_page]
    )

# Global filter
# Sidebar: Pilih filter
st.sidebar.title("🔍 Filters")

# Sidebar: Filter Rentang Tanggal
selected_date_range = st.sidebar.date_input(
    "Select Date Range",
    st.session_state.selected_date_range,
    min_value=min_date,
    max_value=max_date)

# Sidebar: Filter Customer City
cities = ["All"] + sorted(cust_df["customer_city"].unique())
selected_city = st.sidebar.selectbox("Select City", cities)

# Sidebar: Filter Customer State
states = ["All"] + sorted(cust_df["customer_state"].unique())
selected_state = st.sidebar.selectbox("Select State", states)

# **Validasi: Hanya boleh memilih salah satu filter**
if selected_city != "All" and selected_state != "All":
    st.sidebar.warning("⚠️ Hanya boleh memilih satu filter: City atau State. Pilih 'All' pada salah satu filter untuk melanjutkan.")


# Update session_state jika ada perubahan & refresh halaman
if (
    selected_date_range != st.session_state.selected_date_range or
    selected_city != st.session_state.selected_city or
    selected_state != st.session_state.selected_state
):
    st.session_state.selected_date_range = selected_date_range
    st.session_state.selected_city = selected_city
    st.session_state.selected_state = selected_state
    st.rerun()  # Refresh agar filter berlaku


# Logo and text
st.logo("./dashboard/assets/Logo-Olist.png")

st.sidebar.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    
    <p style='text-align: center; font-size: 10px; color: gray;'>
        © 2025 <b>Brazilian E-commerce Dashboard</b><br>
        Dicoding Submission - Ach. Arif Setiawan
    </p>
    <p style='text-align: center; font-size: 18px;'>
        <a href="https://www.linkedin.com/in/ach-arif-setiawan" target="_blank" style="color: #FAFAFA; text-decoration: none; margin-right: 15px;">
            <i class="fa-brands fa-linkedin"></i>
        </a>
        <a href="https://github.com/Setyawant" target="_blank" style="color: #FAFAFA; text-decoration: none;">
            <i class="fa-brands fa-github"></i>
        </a>
    </p>
    """,
    unsafe_allow_html=True
)

pg.run()

