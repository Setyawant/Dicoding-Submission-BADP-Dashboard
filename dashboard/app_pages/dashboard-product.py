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

# Hitung kategori produk paling laris berdasarkan jumlah order
top_selling_category = (
    filtered_city_state.groupby("product_category_name_english")["order_id"].count()
    .reset_index().sort_values(by="order_id", ascending=False).iloc[0])
top_selling_name = top_selling_category["product_category_name_english"]
top_selling_value = top_selling_category["order_id"]

# Hitung kategori dengan rating tertinggi (rata-rata rating tertinggi)
top_rated_category = (
    filtered_city_state.groupby("product_category_name_english")["review_score"].mean()
    .reset_index().sort_values(by="review_score", ascending=False).iloc[0])
top_rated_name = top_rated_category["product_category_name_english"]
top_rated_value = f"{top_rated_category['review_score']:.1f}/5"

# Hitung kategori dengan jumlah ulasan terbanyak
most_reviewed_category = (
    filtered_city_state.groupby("product_category_name_english")["review_id"].count()
    .reset_index().sort_values(by="review_id", ascending=False).iloc[0])
most_reviewed_name = most_reviewed_category["product_category_name_english"]
most_reviewed_value = most_reviewed_category["review_id"]

# Line Chart - Tren jumlah produk yang terjual per bulan.
# Hitung total penjualan per kategori produk
top_categories = (filtered_city_state.groupby("product_category_name_english")["order_item_id"].count().nlargest(5).index)

# Filter data hanya untuk 5 kategori teratas
monthly_sales_trend_top5 = (filtered_city_state[filtered_city_state["product_category_name_english"].isin(top_categories)]
                            .groupby(["year_month", "product_category_name_english"])["order_item_id"].count().reset_index())

# Buat Line Chart untuk 5 kategori teratas
fig_sales_trend_top5 = px.line(monthly_sales_trend_top5, x="year_month", y="order_item_id", 
                               color="product_category_name_english", markers=True,
                               color_discrete_sequence=px.colors.qualitative.Prism,
                               labels={
                                   "year_month": "Month", 
                                   "order_item_id": "Total Products Sold", 
                                   "product_category_name": "Product Category"})

fig_sales_trend_top5.update_layout(xaxis_title=None, yaxis_title="Total Products Sold", xaxis_tickangle=-45)

# Bar Chart - Top 5 Kategori Produk dengan Pendapatan Tertinggi
# Hitung total pendapatan per kategori produk
top_categories_revenue = (filtered_city_state.groupby("product_category_name_english")["payment_value"]
                          .sum().reset_index().sort_values(by="payment_value", ascending=False).head(5))

# Buat Bar Chart
fig_top_categories_revenue = px.bar(top_categories_revenue, x="payment_value", y="product_category_name_english",
                                    orientation="h", labels={"payment_value": "Total Revenue (R$)", "product_category_name_english": "Product Category"},
                                    color="product_category_name_english", color_discrete_sequence=px.colors.qualitative.Prism)

# Perbaiki tampilan
fig_top_categories_revenue.update_layout(yaxis=dict(categoryorder="total ascending"), showlegend=False)


# Bar Chart - Top 5 Produk dengan Jumlah Penjualan Tertinggi
# Hitung jumlah penjualan per produk
top_products_sales = (filtered_city_state.groupby("product_id")["order_item_id"]
                      .count().reset_index()
                      .sort_values(by="order_item_id", ascending=False)
                      .head(5))  # Ambil Top 5 Produk

# Buat Bar Chart dengan product_id sebagai label
fig_top_products_sales = px.bar(top_products_sales, x="order_item_id", y="product_id",
                                orientation="h", color="product_id",
                                labels={"order_item_id": "Total Sales", "product_id": "Product ID"},
                                color_discrete_sequence=px.colors.qualitative.Prism)

# Perbaiki tampilan agar urutan dari atas ke bawah
fig_top_products_sales.update_layout(yaxis=dict(categoryorder="total ascending"), showlegend=False)

#################### Streamlit UI Code ####################
# Judul halaman home
st.title("Brazilian E-commerce Dashboard 📊")
st.subheader("🛍️ Product Analysis")

# Menampilkan metrik utama
st.metric("Top Selling Category", f"🔥 {top_selling_name} ({top_selling_value} sales)", help="Kategori produk dengan jumlah order terbanyak.", border=True)
st.metric("Top Rated Category", f"⭐ {top_rated_name} ({top_rated_value})", help="Kategori produk dengan rating rata-rata tertinggi.", border=True)
st.metric("Most Reviewed Category", f"💬 {most_reviewed_name} ({most_reviewed_value} reviews)", help="Kategori produk dengan jumlah ulasan terbanyak.", border=True)

st.subheader("Top 5 Product Categories Sales Trend per Month")
st.plotly_chart(fig_sales_trend_top5, use_container_width=True)

col1a, col2a = st.columns(2)

with col1a:
    st.subheader("Top 5 Product Categories by Revenue")
    st.plotly_chart(fig_top_categories_revenue, use_container_width=True)

with col2a:
    st.subheader("Top 5 Most Purchased Products Based on Sales Count")
    st.plotly_chart(fig_top_products_sales, use_container_width=True)
