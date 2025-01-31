# **📊 Brazilian E-Commerce Dashboard**

## **1️⃣ Project Overview**

### **📌 Tentang Proyek**

Brazilian E-Commerce Dashboard adalah aplikasi berbasis **Streamlit** yang dirancang untuk menganalisis performa e-commerce Brasil menggunakan **[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)**. Dashboard ini menyajikan berbagai metrik, visualisasi, serta analisis berbasis data untuk memahami tren pesanan, perilaku pelanggan, performa penjual, dan lainnya.

### **🎯 Tujuan Proyek**

- Memvisualisasikan data e-commerce untuk memberikan wawasan yang lebih dalam kepada pemangku kepentingan.
- Mengidentifikasi pola pembelian pelanggan berdasarkan segmentasi dan metrik RFM.
- Menganalisis kinerja penjual, produk terlaris, serta metode pembayaran yang paling sering digunakan.
- Menampilkan analisis ulasan pelanggan untuk memahami kepuasan pengguna.
- Menyediakan insights berbasis geospasial menggunakan peta interaktif.

### **🛠️ Teknologi yang Digunakan**

✅ **Python** → Pemrosesan data & analisis  
✅ **Pandas, NumPy** → Manipulasi dan analisis data  
✅ **Streamlit** → Pembuatan dashboard interaktif  
✅ **Plotly, Matplotlib, Seaborn** → Visualisasi data  
✅ **Wordcloud** → Pembuatan wordcloud

---

## **2️⃣ Dashboard Structure**

Dashboard memiliki 7 menu utama:

🏠 **Home** → Ringkasan proyek dan gambaran umum dataset.  
📦 **Orders Overview** → Analisis status pesanan, waktu pengiriman, dan jumlah transaksi.  
🛒 **Customers Analysis** → Segmentasi pelanggan berdasarkan **RFM (Recency, Frequency, Monetary)**.  
🏬 **Sellers Performance** → Kinerja penjual berdasarkan jumlah transaksi dan pendapatan.  
🛍️ **Product Analysis** → Produk terlaris, harga rata-rata, ulasan, dan distribusi produk.  
💳 **Payments & Revenue** → Metode pembayaran yang paling sering digunakan dan pendapatan keseluruhan.  
⭐ **Reviews & Ratings** → Analisis sentimen pelanggan berdasarkan ulasan dan rating produk.

---

## **3️⃣ Project Structure**

```
📦Dicoding-Submission-Brazilian-ECommerce-Dashboard
 ┣ 📂dashboard
 ┃ ┣ 📂.streamlit
 ┃ ┃ ┗ 📜config.toml
 ┃ ┣ 📂app_pages
 ┃ ┃ ┣ 📜dashboard-customer.py
 ┃ ┃ ┣ 📜dashboard-home.py
 ┃ ┃ ┣ 📜dashboard-order.py
 ┃ ┃ ┣ 📜dashboard-payment.py
 ┃ ┃ ┣ 📜dashboard-product.py
 ┃ ┃ ┣ 📜dashboard-review.py
 ┃ ┃ ┗ 📜dashboard-seller.py
 ┃ ┣ 📂assets
 ┃ ┃ ┣ 📜dashboard-preview.gif
 ┃ ┃ ┗ 📜Logo-Olist.png
 ┃ ┣ 📜all_rfm_cust_data.csv
 ┃ ┗ 📜dashboard-brazilian-ecommerce.py
 ┣ 📂data
 ┃ ┣ 📜olist_customers_dataset.csv
 ┃ ┣ 📜olist_geolocation_dataset.csv
 ┃ ┣ 📜olist_orders_dataset.csv
 ┃ ┣ 📜olist_order_items_dataset.csv
 ┃ ┣ 📜olist_order_payments_dataset.csv
 ┃ ┣ 📜olist_order_reviews_dataset.csv
 ┃ ┣ 📜olist_products_dataset.csv
 ┃ ┣ 📜olist_sellers_dataset.csv
 ┃ ┗ 📜product_category_name_translation.csv
 ┣ 📜notebook-brazilian-ecommerce.ipynb
 ┣ 📜README.md
 ┣ 📜requiemwnts.txt
 ┗ 📜url.txt
```

---

## **4️⃣ Installation & Usage**

### **📦 Install Dependencies**

```
pip install -r requirements.txt
```

### **🚀 Run Streamlit Dashboard**

```
streamlit run dashboard-brazilian-ecommerce.py
```

---

## **5️⃣ Dashboard Preview**

Brazilian E-Commerce Dashboard dapat diakses melalui tautan berikut:

🔗 **[Lihat Dashboard di Streamlit Cloud](https://dicoding-submission-badp-dashboard-setyawant.streamlit.app/)**

![Demo](./dashboard/assets/dashboard-preview.gif)

---

<p align="center">Thanks for visiting my project! 🚀🔥</p>

---
