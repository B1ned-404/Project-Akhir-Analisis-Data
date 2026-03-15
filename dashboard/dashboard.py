import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


# LOAD DATA

customer_orders = pd.read_csv("./dashboard/customer_orders_cleaned.csv")
customer_reviews = pd.read_csv("./dashboard/customer_review_cleaned.csv")
payment_method = pd.read_csv("./dashboard/payment_method_cleaned.csv")
product_catalog = pd.read_csv("./dashboard/product_catalog_cleaned.csv")
product_order = pd.read_csv("./dashboard/product_orders_cleaned.csv")

# convert datetime
customer_orders["order_purchase_timestamp"] = pd.to_datetime(
    customer_orders["order_purchase_timestamp"]
)

# MERGE DATA FOR ANALYSIS

product_identification = product_order.merge(
    product_catalog,
    on="product_id",
    how="left"
)

# STREAMLIT TITLE

st.title("E-Commerce Data Analysis Dashboard")

# 1 TOP 10 PRODUCT REVENUE

st.subheader("Top 10 Products Contributing to Revenue")

product = (
'beleza_saude','relogios_presentes','cama_mesa_banho','esporte_lazer',
'informatica_acessorios','moveis_decoracao','cool_stuff',
'utilidades_domesticas','automotivo','ferramentas_jardim'
)

revenue = (
1258681.34,1205005.68,1036988.68,988048.97,911954.32,
729762.49,635290.85,632248.66,592720.11,485256.46
)

fig, ax = plt.subplots(figsize=(10,6))

bars = ax.bar(product, revenue)

plt.ticklabel_format(style='plain', axis='y')

plt.xticks(rotation=45)

for bar, value in zip(bars, revenue):
    ax.text(
        bar.get_x()+bar.get_width()/2,
        bar.get_height(),
        f'{value/1e6:.2f}M',
        ha='center',
        va='bottom',
        fontsize=9
    )

ax.set_title("Top 10 Products Contributes to Company's Revenue")
ax.set_xlabel("Product Category")
ax.set_ylabel("Revenue")

st.pyplot(fig)

# 2 CUSTOMER REVIEW DISTRIBUTION

st.subheader("Customer Review Rating Distribution")

ratings = customer_reviews["review_score"].value_counts().sort_index()

colors = ['red','orange','gray','lightgreen','green']

labels = ['1 Star','2 Stars','3 Stars','4 Stars','5 Stars']

fig2, ax2 = plt.subplots(figsize=(7,7))

wedges, texts, autotexts = ax2.pie(
    ratings,
    autopct='%1.1f%%',
    startangle=90,
    colors=colors
)

ax2.set_title("Customer Review Rating Distribution")

ax2.legend(
    wedges,
    labels,
    title="Ratings",
    loc="center left",
    bbox_to_anchor=(1,0.5)
)

st.pyplot(fig2)

# 3 RFM ANALYSIS

st.subheader("Customer Segmentation Based on RFM")

top_products = (
    product_identification
    .groupby(["product_id","product_category_name"])
    .agg(total_revenue=("price","sum"))
    .reset_index()
    .sort_values(by="total_revenue", ascending=False)
    .head(10)
)

top_product_ids = top_products["product_id"]

top_product_sales = product_identification[
    product_identification["product_id"].isin(top_product_ids)
]

rfm_data = top_product_sales.merge(
    customer_orders,
    on="order_id",
    how="left"
)

snapshot_date = rfm_data["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

rfm = rfm_data.groupby("customer_id").agg({

    "order_purchase_timestamp": lambda x: (snapshot_date - x.max()).days,
    "order_id": "nunique",
    "price": "sum"

})

rfm.columns = ["Recency","Frequency","Monetary"]

rfm = rfm.reset_index()

rfm["R_score"] = pd.qcut(rfm["Recency"],4,labels=[4,3,2,1])
rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"),4,labels=[1,2,3,4])
rfm["M_score"] = pd.qcut(rfm["Monetary"],4,labels=[1,2,3,4])

rfm["RFM_score"] = (
    rfm["R_score"].astype(str)+
    rfm["F_score"].astype(str)+
    rfm["M_score"].astype(str)
)

# CUSTOMER SEGMENT

def segment_customer(row):

    if row["RFM_score"] == "444":
        return "Champions"

    elif int(row["R_score"]) >= 3 and int(row["F_score"]) >= 3:
        return "Loyal Customers"

    elif int(row["R_score"]) >= 3:
        return "Potential Loyalists"

    else:
        return "At Risk"

rfm["Segment"] = rfm.apply(segment_customer,axis=1)

segment_counts = rfm["Segment"].value_counts()

fig3, ax3 = plt.subplots(figsize=(7,7))

wedges, texts, autotexts = ax3.pie(
    segment_counts,
    autopct='%1.1f%%'
)

ax3.set_title("Customer Segmentation Based on RFM (Top 10 Revenue Products)")

ax3.legend(
    wedges,
    segment_counts.index,
    title="Customer Segment",
    loc="center left",
    bbox_to_anchor=(1,0.5)
)

st.pyplot(fig3)