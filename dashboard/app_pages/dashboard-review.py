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

# Menghitung skor ulasan rata-rata
avg_review_score = filtered_city_state["review_score"].mean()

# Menghitung jumlah total ulasan
total_reviews_count = filtered_city_state["review_score"].count()




#################### Streamlit UI Code ####################
# Judul halaman home
st.title("Brazilian E-commerce Dashboard 📊")
st.subheader("⭐ Reviews & Ratings")

# Membuat kolom untuk metrik
col1a, col2a = st.columns(2)

col1a.metric("Average Review Score", f"⭐ {avg_review_score:.2f}", help="Rata-rata skor ulasan yang diberikan pelanggan.", border=True)
col2a.metric("Total Reviews Count", f"📝 {total_reviews_count:,}", help="Jumlah total ulasan yang diberikan pelanggan.", border=True)

# Membuat filter multiselect segment customer
customer_segments = filtered_city_state["Customer_segment"].unique()
selected_segments = st.multiselect("Select Customer Segments:", customer_segments, default=customer_segments)

# Pie Chart - Distribusi Rating Ulasan
# Filter data berdasarkan customer segment yang dipilih
filtered_segment_city = filtered_city_state[filtered_city_state["Customer_segment"].isin(selected_segments)]
filtered_segment_date = filtered_date[filtered_date["Customer_segment"].isin(selected_segments)]

# Hitung distribusi rating ulasan
review_distribution = filtered_segment_city["review_score"].value_counts().reset_index()
review_distribution.columns = ["Review Score", "Count"]

# Buat Pie Chart untuk distribusi rating ulasan
fig_review_pie = px.pie(review_distribution, 
                         names="Review Score", 
                         values="Count", 
                         color_discrete_sequence=px.colors.qualitative.Prism, 
                         hole=0.4)

fig_review_pie.update_traces(textinfo="label+percent")
fig_review_pie.update_layout(showlegend=False)

# Wordcloud - Frekuensi kata yang muncul
# Ambil hanya ulasan yang tidak kosong dan bukan "NoComment"
filtered_reviews = filtered_segment_city[
    (filtered_segment_city["review_comment_message"].notna()) & 
    (filtered_segment_city["review_comment_message"] != "NoComment")
]["review_comment_message"]

# Gabungkan semua teks ulasan menjadi satu string
text = " ".join(filtered_reviews.astype(str))

# Hapus stopwords umum (bisa disesuaikan)
stopwords = set(STOPWORDS)

# Buat Word Cloud
wordcloud = WordCloud(width=800, height=500, 
                      mode="RGBA", background_color=None,
                      stopwords=stopwords, colormap="viridis", max_words=100).generate(text)


# Choropleth Map - Rata-rata Skor Ulasan per State
# Mengambil data GeoJSON untuk peta negara bagian Brasil
br_geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
# Hitung rata-rata skor ulasan per provinsi dan customer segment
avg_review_per_state = filtered_segment_date.groupby("customer_state")["review_score"].mean().reset_index()

# Buat Choropleth Map untuk rata-rata skor ulasan per provinsi
fig_review_map = px.choropleth(avg_review_per_state, geojson=br_geojson_url, 
                                locations="customer_state", featureidkey="properties.sigla",
                                color="review_score", hover_name="customer_state", 
                                color_continuous_scale="Viridis", 
                                labels={"review_score": "Average Review Score"})

fig_review_map.update_geos(fitbounds="locations", visible=False)
fig_review_map.update_layout(paper_bgcolor="rgba(0,0,0,0)", geo=dict(bgcolor="rgba(0,0,0,0)"))

# Membuat kolom untuk plot
col1b, col2b = st.columns([1, 2])

with col1b:
    st.subheader("Distribution of Review Score")
    st.plotly_chart(fig_review_pie, use_container_width=True)

with col2b:
    st.subheader("Most Frequent Words in Customer Reviews")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
    
st.subheader("Average Review Score by State")
st.plotly_chart(fig_review_map, use_container_width=True)
