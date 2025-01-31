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

# Menghitung rata-rata total transaksi pembayaran
avg_payment_transactions = filtered_city_state["payment_value"].mean()

# Menentukan metode pembayaran yang paling sering digunakan
most_used_payment_method = (filtered_city_state["payment_type"]
                            .value_counts()
                            .idxmax()) 

# Menghitung rata-rata cicilan per transaksi
avg_installments_per_transaction = filtered_city_state["payment_installments"].mean()

# Pie Chart - Distribusi Metode Pembayaran
# Hitung distribusi metode pembayaran
payment_distribution = filtered_city_state["payment_type"].value_counts().reset_index()
payment_distribution.columns = ["payment_type", "count"]

# Buat Pie Chart
fig_payment_pie = px.pie(payment_distribution, 
                          names="payment_type", 
                          values="count", 
                          color_discrete_sequence=px.colors.qualitative.Prism)

# Line Chart - Tren Revenue Bulanan
# Hitung total revenue per bulan per metode pembayaran
monthly_revenue_trend = (filtered_city_state.groupby(["year_month", "payment_type"])["payment_value"]
                         .sum().reset_index())

# Buat Line Chart dengan warna berbeda untuk setiap metode pembayaran
fig_revenue_trend = px.line(monthly_revenue_trend, 
                            x="year_month", 
                            y="payment_value", 
                            color="payment_type",
                            markers=True,  
                            labels={
                                "year_month": "Month", 
                                "payment_value": "Total Revenue (R$)",
                                "payment_type": "Payment Method"
                            },
                            color_discrete_sequence=px.colors.qualitative.Prism)

# Perbaiki tampilan
fig_revenue_trend.update_layout(xaxis_title=None, yaxis_title="Revenue (R$)", xaxis_tickangle=-45)

#################### Streamlit UI Code ####################
# Judul halaman home
st.title("Brazilian E-commerce Dashboard 📊")
st.subheader("💳 Payments & Revenue")

# Membuat kolom untuk metrik
col1a, col2a, col3a = st.columns(3)

col1a.metric("Average Payment Transactions", f"💰 R$ {avg_payment_transactions:,.2f}", help="Rata-rata nilai transaksi pembayaran per order.", border=True)
col2a.metric("Most Used Payment Method", f"💳 {most_used_payment_method}", help="Metode pembayaran yang paling sering digunakan oleh pelanggan.", border=True)
col3a.metric("Average Installment per Transaction", f"📆 {avg_installments_per_transaction:.0f}", help="Rata-rata jumlah cicilan yang dipilih oleh pelanggan per transaksi.", border=True)

# Membuat kolom untuk plot
col1b, col2b = st.columns([1, 2])

with col1b:
    st.subheader("Payment Method Distribution")
    st.plotly_chart(fig_payment_pie)

with col2b:
    st.subheader("Monthly Revenue Trend by Payment Method")
    st.plotly_chart(fig_revenue_trend)

st.subheader("Total Payment Value by State")

# Filter multiselect metode pembayaran
payment_methods = filtered_date["payment_type"].dropna().unique()
selected_payments = st.multiselect("Select Payment Methods:", payment_methods, default=payment_methods)

# Filter dataset berdasarkan metode pembayaran yang dipilih
filtered_payment_data = filtered_date[filtered_date["payment_type"].isin(selected_payments)]

# Hitung total payment value per customer_state
payment_distribution = (filtered_payment_data.groupby("customer_state")["payment_value"]
                        .sum().reset_index())
payment_distribution.columns = ["customer_state", "total_payment_value"]

# Choropleth Map - Total Payment Value per Provinsi
# Load GeoJSON untuk peta Brasil
br_geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
fig_payment_map = px.choropleth(payment_distribution, 
                                geojson=br_geojson_url, 
                                locations='customer_state', 
                                featureidkey="properties.sigla",
                                color='total_payment_value', 
                                hover_name='customer_state',
                                color_continuous_scale=px.colors.sequential.Viridis,
                                labels={"total_payment_value": "Total Payment Value (R$)"})

# Sesuaikan tampilan peta
fig_payment_map.update_geos(fitbounds="locations", visible=False)
fig_payment_map.update_layout(paper_bgcolor="rgba(0,0,0,0)", geo=dict(bgcolor="rgba(0,0,0,0)"))

st.plotly_chart(fig_payment_map)

