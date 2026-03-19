# Proyek Analisis Data: E - Commerce Public Dataset
- **Nama:** Ronan Julius Adiwinata
- **Email:** ronan.adiwinata@binus.ac.id
- **ID Dicoding:** CDCC005D6Y2302

# Project Overview
Project ini dikerjakan untuk menganalisis data penjualan E - Commerce yang berasal dari Kaggle bertujuan untuk melatih kemampuan analisis data serta business sense saya melalui tahapan - tahapan seperti menjabarkan pertanyaan business, wrangling data, assessing data, cleaning data, EDA, Visualisasi dan akhirnya melakukan analisis lanjutan seperti menggunakan teknik RFM Analysis. Berikut merupakan pertanyaan bisnis yang saya jabarkan dan solusi yang diberikan melalui notebook.ipynb (secara terpisah):
1. Jenis produk apa yang memberikan kontribusi pendapatan/revenue terbesar kepada perusahaan?
2. Berapa percentase *retention rate* / tingkat retensi pada customer di dalam ecosystem perusahaan?

# Project Structure
PROJECT-AKHIR-ANALISIS-DATA
├───dashboard
| ├───customer_orders_cleaned.csv
| ├───customer_review_cleaned.csv
| ├───payment_method_cleaned.csv
| ├───product_catalog_cleaned.csv
| ├───product_orders_cleaned.csv
| └───dashboard.py
├───data
| ├───order_items_dataset.csv
| ├───order_payments_dataset.csv
| ├───order_reviews_dataset.csv
| ├───orders_dataset.csv
| └───products_dataset.csv
├───notebook.ipynb
├───README.md
└───requirements.txt
└───url.txt

## Setup Environment - Terminal
```
mkdir Project Akhir Analisis Data
cd Project Akhir Analisis Data
pip install -r requirements.txt
pip freeze requirements.txt

```

## Run steamlit app
```
streamlit run dashboard/dashboard.py
```
