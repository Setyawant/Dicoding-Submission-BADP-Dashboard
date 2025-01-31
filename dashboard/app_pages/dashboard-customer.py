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

# Total Active Customers - Pelanggan yang melakukan lebih dari satu pembelian
active_customers = filtered_city_state["customer_unique_id"].value_counts()
total_active_customers = (active_customers > 1).sum()

# Average Monetary Value - Rata-rata nilai pembelian per pelanggan
avg_monetary_value = filtered_city_state.groupby("customer_unique_id")["payment_value"].sum().mean()

# Customer Retention Rate Tingkat retensi pelanggan
total_customers = filtered_city_state["customer_unique_id"].nunique()
retained_customers = total_active_customers  # Karena mereka melakukan pembelian lebih dari 1 kali
customer_retention_rate = (retained_customers / total_customers) * 100 if total_customers > 0 else 0

# Konversi ke format string
avg_monetary_value_str = f"R$ {avg_monetary_value:,.2f}"
customer_retention_rate_str = f"{customer_retention_rate:.2f}%"

# Scatter Plot - RFM Score vs Revenue
fig_scatter = px.scatter(filtered_city_state, x="RFM_Score", y="Monetary",
                         color="Customer_segment",  # Warna berdasarkan segmentasi pelanggan
                         labels={"RFM_Score": "RFM Score", "Monetary": "Revenue (R$)"},
                         color_discrete_sequence=px.colors.qualitative.Prism,
                         hover_data=["customer_unique_id"])

# Pie Chart - Proporsi Segmentasi Pelanggan
# Hitung proporsi segmentasi pelanggan
customer_segment_counts = filtered_city_state["Customer_segment"].value_counts().reset_index()
customer_segment_counts.columns = ["Customer_segment", "count"]

fig_pie = px.pie(customer_segment_counts, names="Customer_segment", values="count",
                 color_discrete_sequence=px.colors.qualitative.Prism)

# Choropleth Map - Distribusi Pelanggan per State
# Mengambil data GeoJSON untuk peta negara bagian Brasil
br_geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
# Hitung jumlah pelanggan unik per State 
customer_distribution = filtered_date.groupby("customer_state")["customer_unique_id"].nunique().reset_index()
customer_distribution.columns = ["customer_state", "unique_customers"]
fig_customers = px.choropleth(customer_distribution, geojson=br_geojson_url, 
                                locations='customer_state', featureidkey="properties.sigla",
                                color='unique_customers', hover_name='customer_state', 
                                color_continuous_scale=px.colors.sequential.Viridis,
                                labels={"unique_customers": "Jumlah Pelanggan"})
fig_customers.update_geos(fitbounds="locations", visible=False)
fig_customers.update_layout(paper_bgcolor="rgba(0,0,0,0)", geo=dict(bgcolor="rgba(0,0,0,0)"))

# Choropleth Map - Average Revenue per State
# Hitung total revenue per State
revenue_distribution = filtered_date.groupby("customer_state")["payment_value"].mean().reset_index()
revenue_distribution.columns = ["customer_state", "total_revenue"]
fig_revenue = px.choropleth(revenue_distribution, geojson=br_geojson_url, 
                                locations='customer_state', featureidkey="properties.sigla",
                                color='total_revenue', hover_name='customer_state', 
                                color_continuous_scale=px.colors.sequential.Viridis,
                                labels={"total_revenue": "Total Revenue (R$)"})
fig_revenue.update_geos(fitbounds="locations", visible=False)
fig_revenue.update_layout(paper_bgcolor="rgba(0,0,0,0)", geo=dict(bgcolor="rgba(0,0,0,0)"))


#################### Streamlit UI Code ####################
# Judul halaman home
st.title("Brazilian E-commerce Dashboard 📊")
st.subheader("🛒 Customers Analysis")

# Membuat kolom untuk metrik
col1a, col2a, col3a = st.columns(3)

col1a.metric("Total Active Customers", f"👥 {total_active_customers:,}", 
             help="Jumlah pelanggan yang telah melakukan lebih dari satu pembelian.", border=True)

col2a.metric("Average Monetary Value", f"💰 {avg_monetary_value_str}", 
             help="Rata-rata nilai transaksi per pelanggan dalam periode tertentu.", border=True)

col3a.metric("Customer Retention Rate", f"🔁 {customer_retention_rate_str}", 
             help="Persentase pelanggan yang kembali bertransaksi dibandingkan total pelanggan.", border=True)


col1b, col2b = st.columns(2)

with col1b:
    st.subheader("Customer Segment Proportion")
    st.plotly_chart(fig_pie, use_container_width=True)

with col2b:
    st.subheader("RFM Score vs Revenue")
    st.plotly_chart(fig_scatter, use_container_width=True)
    
col1c, col2c = st.columns(2)

with col1c:
    st.subheader("Customer Distribution by State")
    st.plotly_chart(fig_customers, use_container_width=True)

with col2c:
    st.subheader("Total Revenue by State")
    st.plotly_chart(fig_revenue, use_container_width=True)