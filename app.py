import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="E-Commerce Data Analysis Dashboard",
    page_icon="🛒",
    layout="wide"
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🛒 E-Commerce Data Analysis Dashboard")
st.write("Interactive dashboard for E-Commerce Sales, Profit and Customer Analysis")


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("data/Ecommerce_clean.csv")

    df["order_date"] = pd.to_datetime(df["order_date"])
    df["delivery_date"] = pd.to_datetime(df["delivery_date"])

    df["year_month"] = df["order_date"].dt.to_period("M")

    df["delivery_days"] = (
        df["delivery_date"] - df["order_date"]
    ).dt.days

    return df


df = load_data()


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("🔍 Filters")


selected_state = st.sidebar.multiselect(
    "Select State",
    options=sorted(df["state"].dropna().unique()),
    default=sorted(df["state"].dropna().unique())
)


selected_category = st.sidebar.multiselect(
    "Select Category",
    options=sorted(df["category"].dropna().unique()),
    default=sorted(df["category"].dropna().unique())
)


selected_status = st.sidebar.multiselect(
    "Select Order Status",
    options=sorted(df["order_status"].dropna().unique()),
    default=sorted(df["order_status"].dropna().unique())
)


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df[
    (df["state"].isin(selected_state)) &
    (df["category"].isin(selected_category)) &
    (df["order_status"].isin(selected_status))
].copy()


# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_sales = filtered_df["sales"].sum()

total_profit = filtered_df["profit"].sum()

total_orders = filtered_df["order_id"].nunique()


if total_orders > 0:
    average_order_value = total_sales / total_orders
else:
    average_order_value = 0


if total_sales > 0:
    profit_margin = (total_profit / total_sales) * 100
else:
    profit_margin = 0


# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.subheader("📌 Key Performance Indicators")


col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Sales",
    f"₹{total_sales:,.0f}"
)

col2.metric(
    "Total Profit",
    f"₹{total_profit:,.0f}"
)

col3.metric(
    "Total Orders",
    f"{total_orders:,}"
)


col4, col5 = st.columns(2)

col4.metric(
    "Average Order Value",
    f"₹{average_order_value:,.0f}"
)

col5.metric(
    "Profit Margin",
    f"{profit_margin:.2f}%"
)


# --------------------------------------------------
# CHECK EMPTY DATA
# --------------------------------------------------

if filtered_df.empty:

    st.warning("No data available for the selected filters.")

else:

    # ==============================================
    # CATEGORY ANALYSIS
    # ==============================================

    st.divider()

    st.subheader("📊 Category Analysis")


    category_summary = (
        filtered_df
        .groupby("category")[["sales", "profit"]]
        .sum()
        .reset_index()
    )


    category_melted = category_summary.melt(
        id_vars="category",
        value_vars=["sales", "profit"],
        var_name="Metric",
        value_name="Amount"
    )


    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        data=category_melted,
        x="category",
        y="Amount",
        hue="Metric",
        ax=ax
    )

    ax.set_title("Sales vs Profit by Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Amount")

    plt.xticks(rotation=45)

    st.pyplot(fig)

    plt.close(fig)


    # ==============================================
    # TOP PRODUCTS
    # ==============================================

    st.divider()

    st.subheader("🏆 Top 10 Products by Sales")


    top_products = (
        filtered_df
        .groupby("product_name")["sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )


    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        x=top_products.values,
        y=top_products.index,
        ax=ax
    )

    ax.invert_yaxis()

    ax.set_title("Top 10 Products by Sales")
    ax.set_xlabel("Total Sales")
    ax.set_ylabel("Product Name")

    st.pyplot(fig)

    plt.close(fig)


    # ==============================================
    # TOP STATES
    # ==============================================

    st.divider()

    st.subheader("🗺️ Top States by Sales")


    top_states = (
        filtered_df
        .groupby("state")["sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )


    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        x=top_states.values,
        y=top_states.index,
        ax=ax
    )

    ax.invert_yaxis()

    ax.set_title("Top 10 States by Sales")
    ax.set_xlabel("Total Sales")
    ax.set_ylabel("State")

    st.pyplot(fig)

    plt.close(fig)


    # ==============================================
    # MONTHLY SALES AND PROFIT
    # ==============================================

    st.divider()

    st.subheader("📈 Monthly Sales and Profit Trend")


    monthly_summary = (
        filtered_df
        .groupby("year_month")[["sales", "profit"]]
        .sum()
        .reset_index()
    )


    monthly_summary["year_month"] = (
        monthly_summary["year_month"].astype(str)
    )


    fig, ax = plt.subplots(figsize=(12, 6))

    sns.lineplot(
        data=monthly_summary,
        x="year_month",
        y="sales",
        marker="o",
        label="Sales",
        ax=ax
    )

    sns.lineplot(
        data=monthly_summary,
        x="year_month",
        y="profit",
        marker="o",
        label="Profit",
        ax=ax
    )

    ax.set_title("Monthly Sales vs Profit")
    ax.set_xlabel("Year-Month")
    ax.set_ylabel("Amount")

    plt.xticks(rotation=90)

    st.pyplot(fig)

    plt.close(fig)


    # ==============================================
    # ORDER STATUS
    # ==============================================

    st.divider()

    st.subheader("📦 Order Status Distribution")


    order_status_count = (
        filtered_df["order_status"]
        .value_counts()
        .reset_index()
    )

    order_status_count.columns = [
        "order_status",
        "count"
    ]


    fig, ax = plt.subplots(figsize=(8, 6))

    sns.barplot(
        data=order_status_count,
        x="order_status",
        y="count",
        ax=ax
    )

    ax.set_title("Order Status Distribution")
    ax.set_xlabel("Order Status")
    ax.set_ylabel("Number of Orders")

    st.pyplot(fig)

    plt.close(fig)


    # ==============================================
    # AGE DISTRIBUTION
    # ==============================================

    st.divider()

    st.subheader("👥 Customer Age Distribution")


    fig, ax = plt.subplots(figsize=(8, 6))

    sns.histplot(
        data=filtered_df,
        x="age",
        bins=10,
        ax=ax
    )

    ax.set_title("Customer Age Distribution")
    ax.set_xlabel("Age")
    ax.set_ylabel("Customer Count")

    st.pyplot(fig)

    plt.close(fig)


    # ==============================================
    # PROFIT BY DISCOUNT
    # ==============================================

    st.divider()

    st.subheader("💸 Average Profit by Discount Percentage")


    fig, ax = plt.subplots(figsize=(8, 6))

    sns.barplot(
        data=filtered_df,
        x="discount_percent",
        y="profit",
        errorbar=None,
        ax=ax
    )

    ax.set_title("Average Profit by Discount Percentage")
    ax.set_xlabel("Discount Percentage")
    ax.set_ylabel("Average Profit")

    st.pyplot(fig)

    plt.close(fig)


    # ==============================================
    # DELIVERY TIME
    # ==============================================

    st.divider()

    st.subheader("🚚 Average Delivery Time by State")


    fig, ax = plt.subplots(figsize=(12, 6))

    sns.barplot(
        data=filtered_df,
        x="state",
        y="delivery_days",
        errorbar=None,
        ax=ax
    )

    ax.set_title("Average Delivery Time by State")
    ax.set_xlabel("State")
    ax.set_ylabel("Average Delivery Days")

    plt.xticks(rotation=45)

    st.pyplot(fig)

    plt.close(fig)


    # ==============================================
    # SALES VS PROFIT
    # ==============================================

    st.divider()

    st.subheader("🔗 Sales vs Profit")


    fig, ax = plt.subplots(figsize=(8, 6))

    sns.scatterplot(
        data=filtered_df,
        x="sales",
        y="profit",
        ax=ax
    )

    ax.set_title("Sales vs Profit")
    ax.set_xlabel("Sales")
    ax.set_ylabel("Profit")

    st.pyplot(fig)

    plt.close(fig)


# --------------------------------------------------
# DATA PREVIEW
# --------------------------------------------------

st.divider()

st.subheader("📄 Filtered Dataset Preview")

st.dataframe(
    filtered_df,
    use_container_width=True
)