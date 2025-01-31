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

# Hitung total pesanan terkirim & dibatalkan
total_delivered = filtered_city_state[filtered_city_state["order_status"] == "delivered"].shape[0]
total_canceled = filtered_city_state[filtered_city_state["order_status"] == "canceled"].shape[0]

# Hitung rata-rata waktu pemrosesan
filtered_city_state["processing_time"] = (filtered_city_state["order_approved_at"] - 
                                          filtered_city_state["order_purchase_timestamp"]).dt.total_seconds()
# Hitung rata-rata waktu pemrosesan dalam detik
avg_processing_seconds = filtered_city_state["processing_time"].mean()
# Konversi ke format X D X H X M
if not np.isnan(avg_processing_seconds):  
    days = int(avg_processing_seconds // 86400)  # 1 Hari = 86400 Detik
    hours = int((avg_processing_seconds % 86400) // 3600)  # Sisa detik dikonversi ke jam
    minutes = int((avg_processing_seconds % 3600) // 60)  # Sisa detik dikonversi ke menit
    avg_processing_time_str = f"{days}D {hours}H {minutes}M"
else:
    avg_processing_time_str = "N/A"

# Bar Chart → Distribusi Status Pesanan
order_status_counts = filtered_city_state["order_status"].value_counts().reset_index()
order_status_counts.columns = ["order_status", "count"]
fig_bar = px.bar(order_status_counts, x="order_status", y="count", 
                     color="order_status", color_discrete_sequence=px.colors.qualitative.Prism)
fig_bar.update_layout(xaxis_title=None, xaxis=dict(showticklabels=False))

# Line Chart - Tren Rata-rata Waktu Pengiriman per Bulan
avg_delivery_trend = filtered_city_state.groupby("year_month")["delivery_time"].mean().reset_index()
avg_delivery_trend.columns = ["year_month", "avg_delivery_time"]
fig_line = px.area(avg_delivery_trend, x="year_month", y="avg_delivery_time", 
                   markers=True, color_discrete_sequence=px.colors.qualitative.Prism)
fig_line.update_layout(xaxis_title=None)

# Tabel Interaktif - Pesanan yang melebihi estimasi pengiriman
filtered_city_state["late_delivery"] = filtered_city_state["order_delivered_customer_date"] > filtered_city_state["order_estimated_delivery_date"]
late_orders = filtered_city_state[filtered_city_state["late_delivery"]]

# Hitung jumlah hari keterlambatan
late_orders["late_days"] = (late_orders["order_delivered_customer_date"] - 
                            late_orders["order_estimated_delivery_date"]).dt.days

# Pilih kolom yang relevan untuk tabel
late_orders_display = late_orders[[
    "order_id", "customer_unique_id", "order_delivered_customer_date", 
    "order_estimated_delivery_date", "late_days", "delivery_time"
]]
# Hitung total detik keterlambatan rata-rata
avg_late_seconds = (late_orders["order_delivered_customer_date"] - late_orders["order_estimated_delivery_date"]).dt.total_seconds().mean()
# Konversi ke Hari, Jam, Menit
if not np.isnan(avg_late_seconds):  
    days = int(avg_late_seconds // 86400)  # 1 Hari = 86400 Detik
    hours = int((avg_late_seconds % 86400) // 3600)  # Sisa detik dikonversi ke jam
    minutes = int((avg_late_seconds % 3600) // 60)  # Sisa detik dikonversi ke menit
    avg_late_time_str = f"{days}D {hours}H {minutes}M"
else:
    avg_late_time_str = "N/A"


# Choropleth Map - Distribusi Order per State
# Mengambil data GeoJSON untuk peta negara bagian Brasil
br_geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
# Menghitung rata-rata order per negara bagian
order_by_state = filtered_date.groupby("customer_state")["order_id"].nunique().reset_index()
order_by_state.columns = ["state", "order count"]
fig_order_state = px.choropleth(order_by_state, geojson=br_geojson_url, 
                                locations='state', featureidkey="properties.sigla",
                                color='order count', hover_name='state', 
                                color_continuous_scale=px.colors.sequential.Viridis,
                                labels={"order_count": "Jumlah Order"})
fig_order_state.update_geos(fitbounds="locations", visible=False)
fig_order_state.update_layout(paper_bgcolor="rgba(0,0,0,0)", geo=dict(bgcolor="rgba(0,0,0,0)"))

# Choropleth Map - Rata-rata Waktu Pengiriman per State
avg_delivery_by_state = filtered_date.groupby("customer_state")["delivery_time"].mean().reset_index()
avg_delivery_by_state.columns = ["state", "avg delivery time"]
fig_avg_delivery_state = px.choropleth(avg_delivery_by_state, geojson=br_geojson_url, 
                                       locations='state', featureidkey="properties.sigla",
                                       color='avg delivery time', hover_name='state', 
                                       color_continuous_scale=px.colors.sequential.Viridis,
                                       labels={"avg_delivery_time": "Hari"})
fig_avg_delivery_state.update_geos(fitbounds="locations", visible=False)
fig_avg_delivery_state.update_layout(paper_bgcolor="rgba(0,0,0,0)", geo=dict(bgcolor="rgba(0,0,0,0)"))


#################### Streamlit UI Code ####################
# Judul halaman home
st.title("Brazilian E-commerce Dashboard 📊")
st.subheader("📦 Orders Overview")

# Membuat kolom untuk metrik
col1a, col2a, col3a = st.columns(3)
col1a.metric("Total Delivered Orders", f"✅ {total_delivered}", 
             help="Jumlah total pesanan yang berhasil dikirim ke pelanggan.", border=True)
col2a.metric("Total Canceled Orders", f"❌ {total_canceled}", 
             help="Jumlah total pesanan yang dibatalkan sebelum pengiriman.", border=True)
col3a.metric("Total Late Orders", f"⚠️ {len(late_orders_display)}", 
             help="Jumlah total pesanan yang melebihi estimasi waktu pengiriman.", border=True)

col1b, col2b = st.columns(2)
col1b.metric("Average Processing Time", f"⏳ {avg_processing_time_str}", 
             help="Rata-rata waktu yang dibutuhkan dari pembayaran hingga pesanan disetujui.", border=True)
col2b.metric("Average Late Time", f"⏳ {avg_late_time_str}", 
             help="Rata-rata keterlambatan pesanan dibandingkan estimasi pengiriman.", border=True)


# Buat dua kolom untuk menampilkan plot
col1c, col2c = st.columns([1, 2])

with col1c:
    st.subheader("Order Status Distribution")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2c:
    st.subheader("Average Delivery Time Trend per Month")
    st.plotly_chart(fig_line, use_container_width=True)

col1d, col2d= st.columns(2)

with col1d:
    st.subheader("Total Number of Orders by State")
    st.plotly_chart(fig_order_state, use_container_width=True)

with col2d:
    st.subheader("Average Delivery Time by State")
    st.plotly_chart(fig_avg_delivery_state, use_container_width=True)

st.subheader("Late Delivery Orders Table")
st.dataframe(late_orders_display, use_container_width=True)