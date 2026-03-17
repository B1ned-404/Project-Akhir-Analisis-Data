import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


# LOAD DATA (relative path — safe to run from any directory)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

customer_orders  = pd.read_csv(os.path.join(BASE_DIR, "customer_orders_cleaned.csv"))
customer_reviews = pd.read_csv(os.path.join(BASE_DIR, "customer_review_cleaned.csv"))
payment_method   = pd.read_csv(os.path.join(BASE_DIR, "payment_method_cleaned.csv"))
product_catalog  = pd.read_csv(os.path.join(BASE_DIR, "product_catalog_cleaned.csv"))
product_order    = pd.read_csv(os.path.join(BASE_DIR, "product_orders_cleaned.csv"))

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

# STREAMLIT PAGE CONFIG

st.set_page_config(
    page_title="E-Commerce Data Analysis Dashboard",
    page_icon="🛒",
    layout="wide",
)

# STREAMLIT TITLE

st.title("E-Commerce Data Analysis Dashboard")


# SIDEBAR — INTERACTIVE WIDGETS 

st.sidebar.header("Filter Data")

# 1. Date range filter
min_date = customer_orders["order_purchase_timestamp"].min().date()
max_date = customer_orders["order_purchase_timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# 2. Product category filter
all_categories = [
    "beleza_saude", "relogios_presentes", "cama_mesa_banho",
    "esporte_lazer", "informatica_acessorios", "moveis_decoracao",
    "cool_stuff", "utilidades_domesticas", "automotivo", "ferramentas_jardim",
]

selected_categories = st.sidebar.multiselect(
    "Product Category",
    options=all_categories,
    default=all_categories,
)

# 3. Minimum review score filter
min_review_score = st.sidebar.slider(
    "Minimum Review Score",
    min_value=1,
    max_value=5,
    value=1,
)

# APPLY FILTERS 

filtered_orders = customer_orders[
    (customer_orders["order_purchase_timestamp"].dt.date >= start_date) &
    (customer_orders["order_purchase_timestamp"].dt.date <= end_date)
]

filtered_reviews = customer_reviews[
    customer_reviews["review_score"] >= min_review_score
]


# 1 TOP 10 PRODUCT REVENUE

st.subheader("Top 10 Products Contributing to Revenue")

revenue_data = {
    "beleza_saude":          1258681.34,
    "relogios_presentes":    1205005.68,
    "cama_mesa_banho":       1036988.68,
    "esporte_lazer":          988048.97,
    "informatica_acessorios": 911954.32,
    "moveis_decoracao":       729762.49,
    "cool_stuff":             635290.85,
    "utilidades_domesticas":  632248.66,
    "automotivo":             592720.11,
    "ferramentas_jardim":     485256.46,
}

# apply category filter
filtered_revenue = {k: v for k, v in revenue_data.items() if k in selected_categories}
sorted_revenue   = dict(sorted(filtered_revenue.items(), key=lambda x: x[1], reverse=True))

product = tuple(sorted_revenue.keys())
revenue = tuple(sorted_revenue.values())

if product:
    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(product, revenue)

    plt.ticklabel_format(style='plain', axis='y')
    plt.xticks(rotation=45, ha='right')

    for bar, value in zip(bars, revenue):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f'{value / 1e6:.2f}M',
            ha='center',
            va='bottom',
            fontsize=9
        )

    ax.set_title("Top 10 Products Contributes to Company's Revenue")
    ax.set_xlabel("Product Category")
    ax.set_ylabel("Revenue")

    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("No category selected. Please select at least one category from the sidebar.")


# 2 CUSTOMER REVIEW DISTRIBUTION

st.subheader("Customer Review Rating Distribution")

ratings = filtered_reviews["review_score"].value_counts().sort_index()

colors_map = {1: 'red', 2: 'orange', 3: 'gray', 4: 'lightgreen', 5: 'green'}
label_map  = {1: '1 Star', 2: '2 Stars', 3: '3 Stars', 4: '4 Stars', 5: '5 Stars'}

colors = [colors_map[i] for i in ratings.index]
labels = [label_map[i] for i in ratings.index]

if not ratings.empty:
    fig2, ax2 = plt.subplots(figsize=(7, 7))

    wedges, texts, autotexts = ax2.pie(
        ratings,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors
    )

    ax2.set_title(f"Customer Review Rating Distribution (Score >= {min_review_score})")

    ax2.legend(
        wedges,
        labels,
        title="Ratings",
        loc="center left",
        bbox_to_anchor=(1, 0.5)
    )

    st.pyplot(fig2)
else:
    st.warning("No review data available for the selected filter.")


# 3 RFM ANALYSIS

st.subheader("Customer Segmentation Based on RFM")

top_products = (
    product_identification
    .groupby(["product_id", "product_category_name"])
    .agg(total_revenue=("price", "sum"))
    .reset_index()
    .sort_values(by="total_revenue", ascending=False)
    .head(10)
)

top_product_ids = top_products["product_id"]

top_product_sales = product_identification[
    product_identification["product_id"].isin(top_product_ids)
]

# use filtered_orders so RFM reflects the selected date range
rfm_data = top_product_sales.merge(
    filtered_orders,
    on="order_id",
    how="inner"
)

if rfm_data.empty:
    st.warning("No RFM data available for the selected date range.")
else:
    snapshot_date = rfm_data["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

    rfm = rfm_data.groupby("customer_id").agg({
        "order_purchase_timestamp": lambda x: (snapshot_date - x.max()).days,
        "order_id": "nunique",
        "price": "sum"
    })

    rfm.columns = ["Recency", "Frequency", "Monetary"]
    rfm = rfm.reset_index()

    rfm["R_score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1])
    rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
    rfm["M_score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4])

    rfm["RFM_score"] = (
        rfm["R_score"].astype(str) +
        rfm["F_score"].astype(str) +
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

    rfm["Segment"] = rfm.apply(segment_customer, axis=1)

    segment_counts = rfm["Segment"].value_counts()

    fig3, ax3 = plt.subplots(figsize=(7, 7))

    wedges, texts, autotexts = ax3.pie(
        segment_counts,
        autopct='%1.1f%%'
    )

    ax3.set_title(
        f"Customer Segmentation Based on RFM (Top 10 Revenue Products)\n"
        f"{start_date} to {end_date}"
    )

    ax3.legend(
        wedges,
        segment_counts.index,
        title="Customer Segment",
        loc="center left",
        bbox_to_anchor=(1, 0.5)
    )

    st.pyplot(fig3)