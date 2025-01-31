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
    cust_df = st.session_state.cust_df
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

# Menghitung Jumlah total penjual unik
total_sellers = filtered_city_state["seller_id"].nunique()

# Menghitung Rata-rata waktu pengiriman per penjual
# Hitung waktu pengiriman per seller (dalam hari)
filtered_city_state["seller_delivery_time"] = (
    filtered_city_state["order_delivered_carrier_date"] - filtered_city_state["order_approved_at"]
).dt.total_seconds() / 86400  # Konversi detik ke hari

# Hitung rata-rata waktu pengiriman per penjual
avg_seller_delivery_time = filtered_city_state.groupby("seller_id")["seller_delivery_time"].mean().mean()

# Konversi ke format X D X H X M
if not np.isnan(avg_seller_delivery_time):
    days = int(avg_seller_delivery_time)
    hours = int((avg_seller_delivery_time % 1) * 24)
    minutes = int(((avg_seller_delivery_time % 1) * 24 % 1) * 60)
    avg_seller_delivery_str = f"{days}D {hours}H {minutes}M"
else:
    avg_seller_delivery_str = "N/A"

# Menghitung Seller Retention Rate
max_year_month = filtered_city_state["year_month"].max()

# Hitung seller retention rate berdasarkan max_year_month
active_sellers = filtered_city_state[filtered_city_state["year_month"] >= max_year_month]["seller_id"].nunique()
initial_sellers = filtered_city_state[filtered_city_state["year_month"] < max_year_month]["seller_id"].nunique()
seller_retention_rate = (active_sellers / initial_sellers) * 100 if initial_sellers > 0 else 0

# Bar Chart - Top 5 Sellers by Order Count
# Hitung jumlah order per seller
top_sellers = filtered_city_state.groupby("seller_id")["order_id"].count().reset_index()
top_sellers = top_sellers.sort_values(by="order_id", ascending=False).head(5)

# Buat Bar Chart
fig_top_sellers = px.bar(top_sellers, x="order_id", y="seller_id",
                         color="seller_id", orientation="h",
                         labels={"order_id": "Total Orders", "seller_id": "Seller ID"},
                         color_discrete_sequence=px.colors.qualitative.Prism)
fig_top_sellers.update_layout(yaxis=dict(categoryorder="total ascending"),
                                       yaxis_title=None, showlegend=False)

# Bar Chart - Top 5 Sellers by Product Count
# Hitung jumlah produk unik per seller
top_sellers_products = filtered_city_state.groupby("seller_id")["product_id"].nunique().reset_index()
top_sellers_products = top_sellers_products.sort_values(by="product_id", ascending=False).head(5)

# Buat Bar Chart
fig_top_sellers_products = px.bar(top_sellers_products, x="product_id", y="seller_id",
                                  color="seller_id", orientation="h",
                                  labels={"product_id": "Total Products", "seller_id": "Seller ID"},
                                  color_discrete_sequence=px.colors.qualitative.Prism)
fig_top_sellers_products.update_layout(yaxis=dict(categoryorder="total ascending"),
                                       yaxis_title=None, showlegend=False)

# Choropleth Map - Sebaran Penjual per Provinsi
# Mengambil data GeoJSON untuk peta negara bagian Brasil
br_geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
# Hitung jumlah seller per provinsi
seller_distribution = filtered_date.groupby("seller_state")["seller_id"].nunique().reset_index()
seller_distribution.columns = ["seller_state", "unique_sellers"]
fig_seller_map = px.choropleth(seller_distribution, geojson=br_geojson_url, 
                              locations='seller_state', featureidkey="properties.sigla",
                              color='unique_sellers', hover_name='seller_state', 
                              color_continuous_scale=px.colors.sequential.Viridis,
                              labels={"unique_sellers": "Total Sellers"})
fig_seller_map.update_geos(fitbounds="locations", visible=False)
fig_seller_map.update_layout(paper_bgcolor="rgba(0,0,0,0)", geo=dict(bgcolor="rgba(0,0,0,0)"))

#################### Streamlit UI Code ####################
# Judul halaman home
st.title("Brazilian E-commerce Dashboard 📊")
st.subheader("🏬 Sellers Performance")

# Membuat kolom untuk metrik
col1a, col2a, col3a = st.columns(3)

col1a.metric("Total Sellers", f"👥 {total_sellers:,}", help="Jumlah total penjual unik di platform", border=True)
col2a.metric("Average Seller Delivery Time", f"⏳ {avg_seller_delivery_str}", help="Rata-rata waktu pengiriman per penjual", border=True)
col3a.metric("Seller Retention Rate", f"🔁 {seller_retention_rate:.2f}%", help="Persentase penjual yang tetap aktif dalam periode tertentu", border=True)

# Membuat kolom untuk plot
col1b, col2b = st.columns(2)

with col1b:
    st.subheader("Top 5 Sellers by Order Count")
    st.plotly_chart(fig_top_sellers, use_container_width=True)

with col2b:
    st.subheader("Top 5 Sellers by Product")
    st.plotly_chart(fig_top_sellers_products, use_container_width=True)

st.subheader("Seller Distribution by State")
st.plotly_chart(fig_seller_map, use_container_width=True)