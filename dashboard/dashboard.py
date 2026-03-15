import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

customer_orders = pd.read_csv("./customer_orders_cleaned.csv")
customer_review = pd.read_csv("./customer_review_cleaned.csv")
payment_method = pd.read_csv("./payment_method_cleaned.csv")
product_catalog = pd.read_csv("./product_catalog_cleaned.csv")
product_orders = pd.read_csv("./product_orders_cleaned.csv")

customer_orders["order_date"] = pd.to_datetime(customer_orders["order_date"])
customer_orders["delivery_date"] = pd.to_datetime(customer_orders["delivery_date"])

min_date = customer_orders["order_date"].min()
max_date = customer_orders["order_date"].max()

with st.sidebar:

    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_orders = customer_orders[
    (customer_orders["order_date"] >= pd.to_datetime(start_date)) &
    (customer_orders["order_date"] <= pd.to_datetime(end_date))
]

def create_daily_orders_df(df):

    daily_orders = df.resample(rule="D", on="order_date").agg({
        "order_id": "nunique",
        "total_price": "sum"
    }).reset_index()

    daily_orders.rename(columns={
        "order_id": "order_count",
        "total_price": "revenue"
    }, inplace=True)

    return daily_orders

def create_product_sales_df(df):

    product_sales = df.groupby("product_id")["quantity"].sum().reset_index()

    return product_sales

def create_gender_df(df):

    gender_df = df.groupby("gender")["customer_id"].nunique().reset_index()

    gender_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)

    return gender_df

def create_rfm_df(df):

    rfm_df = df.groupby("customer_id", as_index=False).agg({
        "order_date": "max",
        "order_id": "nunique",
        "total_price": "sum"
    })

    rfm_df.columns = ["customer_id", "last_order", "frequency", "monetary"]

    recent_date = df["order_date"].max()

    rfm_df["recency"] = (recent_date - rfm_df["last_order"]).dt.days

    return rfm_df

daily_orders_df = create_daily_orders_df(filtered_orders)

product_sales_df = create_product_sales_df(product_orders)

gender_df = create_gender_df(customer_orders)

rfm_df = create_rfm_df(customer_orders)

st.header("Dicoding Collection Dashboard :sparkles:")

st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df["order_count"].sum()
    st.metric("Total Orders", total_orders)

with col2:
    total_revenue = format_currency(
        daily_orders_df["revenue"].sum(),
        "AUD",
        locale="es_CO"
    )
    st.metric("Total Revenue", total_revenue)

    fig, ax = plt.subplots(figsize=(16,8))

ax.plot(
    daily_orders_df["order_date"],
    daily_orders_df["order_count"],
    marker="o",
    color="#90CAF9"
)

st.pyplot(fig)

st.subheader("Product Sales")

fig, ax = plt.subplots(figsize=(12,6))

top_products = product_sales_df.sort_values(
    by="quantity",
    ascending=False
).head(10)

sns.barplot(
    x="quantity",
    y="product_id",
    data=top_products,
    color="#90CAF9",
    ax=ax
)

st.pyplot(fig)

st.subheader("Customer Demographics")

fig, ax = plt.subplots()

sns.barplot(
    x="gender",
    y="customer_count",
    data=gender_df,
    palette=["#90CAF9","#D3D3D3"],
    ax=ax
)

st.pyplot(fig)

st.subheader("Best Customer Based on RFM")

top_customers = rfm_df.sort_values(
    by="monetary",
    ascending=False
).head(5)

fig, ax = plt.subplots()

sns.barplot(
    x="customer_id",
    y="monetary",
    data=top_customers,
    color="#90CAF9",
    ax=ax
)

st.pyplot(fig)

