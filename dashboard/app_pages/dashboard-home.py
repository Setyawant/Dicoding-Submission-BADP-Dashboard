import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud, STOPWORDS


#################### Data Processing Code ####################
# Ambil data dari session_state
if "cust_df" not in st.session_state:
    st.error("Data belum dimuat! Silakan jalankan main.py terlebih dahulu.")
else:
    cust_df = st.session_state.cust_df

# Ambil filter dari session_state
selected_date_range = st.session_state.get("selected_date_range", None)
selected_city = st.session_state.get("selected_city", "All")
selected_state = st.session_state.get("selected_state", "All")

# Filter data berdasarkan rentang tanggal
# Pastikan filter tanggal dalam bentuk datetime
start_date = pd.to_datetime(selected_date_range[0])
end_date = pd.to_datetime(selected_date_range[1])

filtered_date = cust_df[
    (cust_df["order_purchase_timestamp"] >= start_date) &
    (cust_df["order_purchase_timestamp"] <= end_date)
]

filtered_city_state = filtered_date.copy()

# Filter berdasarkan Customer City jika dipilih
if selected_city != "All":
    filtered_city_state = filtered_city_state[filtered_city_state["customer_city"] == selected_city]

# Filter berdasarkan Customer State jika dipilih
if selected_state != "All":
    filtered_city_state = filtered_city_state[filtered_city_state["customer_state"] == selected_state]

# Hitung rata-rata waktu pengiriman
average_delivery_time = filtered_city_state["delivery_time"].mean()

# Line Chart - Tren Jumlah Pesanan per Bulan
order_trend = filtered_city_state.groupby("year_month").size().reset_index(name="order_count")
fig_tren = px.area(order_trend, x="year_month", y="order_count",
                   labels={"year_month": "Bulan", "order_count": "order count"},
                   markers=True, color_discrete_sequence=px.colors.qualitative.Prism)
fig_tren.update_layout(xaxis_title=None)


# Pie Chart - Distribusi Order Berdasarkan Status
order_status_counts = filtered_city_state["order_status"].value_counts().reset_index()
order_status_counts.columns = ["order_status", "count"]
fig_pie = px.pie(order_status_counts, names="order_status", values="count", title=" ",
                 color_discrete_sequence=px.colors.qualitative.Prism)

# Bar Chart - Top 5 Kota dengan Pesanan Terbanyak
top_cities = filtered_date["customer_city"].value_counts().nlargest(5).reset_index()
top_cities.columns = ["customer_city", "order count"]
fig_bar_city = px.bar(top_cities, x="order count", y="customer_city",
                 color="customer_city", orientation="h",
                 color_discrete_sequence=px.colors.qualitative.Prism)
fig_bar_city.update_layout(yaxis_title=None, yaxis=dict(showticklabels=False))


# Bar Chart - Top 5 State dengan Pesanan Terbanyak
top_states = filtered_date["customer_state"].value_counts().nlargest(5).reset_index()
top_states.columns = ["customer_state", "order count"]
fig_bar_state = px.bar(top_states, x="order count", y="customer_state",
                 color="customer_state", orientation="h",
                 color_discrete_sequence=px.colors.qualitative.Prism)
fig_bar_state.update_layout(yaxis_title=None, yaxis=dict(showticklabels=False))

#################### Streamlit UI Code ####################
# Judul halaman home
st.title("Brazilian E-commerce Dashboard 📊")
st.subheader("🏠 Home")

# Membuat kolom untuk metrik
col1a, col2a, col3a = st.columns(3)
col1a.metric("Total Orders", f"📦 {filtered_city_state['order_id'].nunique()}", 
             help="Total jumlah pesanan unik yang dilakukan oleh pelanggan.", border=True)
col2a.metric("Total Customers", f"👥 {filtered_city_state['customer_unique_id'].nunique()}", 
             help="Jumlah pelanggan unik yang melakukan setidaknya satu transaksi.", border=True)
col3a.metric("Total Sellers", f"🏬 {filtered_city_state['seller_id'].nunique()}", 
             help="Jumlah total penjual unik yang beroperasi di platform.", border=True)

col1b, col2b = st.columns(2)
col1b.metric("Total Revenue", f"💰 R$ {filtered_city_state['payment_value'].sum():,.0f}", 
             help="Total pendapatan yang dihasilkan dari semua transaksi.", border=True)
col2b.metric("Average Delivery Time", f"🚚 {average_delivery_time:,.0f} Days", 
             help="Rata-rata waktu pengiriman dari pesanan dibuat hingga diterima pelanggan.", border=True)


# Membuat kolom untuk plot
col1c, col2c = st.columns([1, 2])

with col1c:
    st.subheader("Order Status Distribution")
    st.plotly_chart(fig_pie, use_container_width=True)

with col2c:
    st.subheader("Order Volume Trend per Month")
    st.plotly_chart(fig_tren)

col1d, col2d = st.columns(2)

with col1d:
    st.subheader("Top 5 Cities by Order Volume")
    st.plotly_chart(fig_bar_city, use_container_width=True)

with col2d:
    st.subheader("Top 5 States by Order Volume")
    st.plotly_chart(fig_bar_state, use_container_width=True)
